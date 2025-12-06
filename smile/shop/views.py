from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg, Count, F
from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import gettext as _
from .models import Product, Category, Cart, CartItem, ProductReview, Wishlist
from .forms import UserRegisterForm, UserUpdateForm, CustomerProfileForm, ContactForm, ProductReviewForm, AdvancedSearchForm
from invoicing.models import Customer, Order


class HomeView(TemplateView):
    """Page d'accueil"""
    template_name = 'shop/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.filter(is_active=True, is_featured=True)[:8]
        context['latest_products'] = Product.objects.filter(is_active=True)[:8]
        context['categories'] = Category.objects.filter(is_active=True, parent=None)[:6]
        return context


class ProductListView(ListView):
    """Liste des produits"""
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        
        # Recherche
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(sku__icontains=search)
            )
        
        # Tri
        sort = self.request.GET.get('sort', '-created_at')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'name':
            queryset = queryset.order_by('name')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        return context


class CategoryView(ListView):
    """Produits par catégorie"""
    model = Product
    template_name = 'shop/category.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'], is_active=True)
        return Product.objects.filter(is_active=True, category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProductDetailView(DetailView):
    """Détail d'un produit"""
    model = Product
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        # Produits similaires
        context['related_products'] = Product.objects.filter(
            is_active=True, 
            category=product.category
        ).exclude(id=product.id)[:4]
        
        # Avis approuvés
        context['reviews'] = product.reviews.filter(is_approved=True).order_by('-created_at')
        context['review_count'] = context['reviews'].count()
        context['average_rating'] = product.average_rating
        context['rating_distribution'] = product.rating_distribution
        
        # Formulaire d'avis
        context['review_form'] = ProductReviewForm()
        
        # Vérifier si l'utilisateur peut laisser un avis
        if self.request.user.is_authenticated:
            context['user_has_reviewed'] = product.reviews.filter(user=self.request.user).exists()
            # Vérifier si achat vérifié
            context['is_verified_purchase'] = Order.objects.filter(
                user=self.request.user,
                items__product=product,
                status__in=['delivered', 'shipped']
            ).exists()
            # Vérifier si dans wishlist
            try:
                wishlist = self.request.user.wishlist
                context['in_wishlist'] = product in wishlist.products.all()
            except Wishlist.DoesNotExist:
                context['in_wishlist'] = False
        else:
            context['user_has_reviewed'] = False
            context['is_verified_purchase'] = False
            context['in_wishlist'] = False
        
        # Variantes disponibles
        context['has_variants'] = product.has_variants
        context['available_attributes'] = product.available_attributes
        
        return context


def get_or_create_cart(request):
    """Récupère ou crée un panier"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def cart_view(request):
    """Vue du panier"""
    cart = get_or_create_cart(request)
    
    # Calcul des totaux
    subtotal = cart.subtotal
    shipping = 0 if subtotal >= settings.FREE_SHIPPING_THRESHOLD else settings.SHIPPING_COST
    tax = subtotal * (settings.TAX_RATE / 100)
    total = subtotal + shipping + tax
    
    context = {
        'cart': cart,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
        'free_shipping_threshold': settings.FREE_SHIPPING_THRESHOLD,
    }
    return render(request, 'shop/cart.html', context)


def add_to_cart(request, product_id):
    """Ajouter au panier"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart = get_or_create_cart(request)
        quantity = int(request.POST.get('quantity', 1))
        
        # Vérifier le stock
        if product.track_stock and product.stock_quantity < quantity:
            messages.error(request, f'Stock insuffisant pour {product.name}')
            return redirect('shop:product_detail', slug=product.slug)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        messages.success(request, f'{product.name} ajouté au panier')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'cart_count': cart.total_items})
        
        return redirect('shop:cart')
    
    return redirect('shop:home')


def update_cart(request, item_id):
    """Mettre à jour la quantité"""
    if request.method == 'POST':
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            item.delete()
            message = 'Article supprimé du panier'
        else:
            if item.product.track_stock and item.product.stock_quantity < quantity:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Stock insuffisant'})
                messages.error(request, 'Stock insuffisant')
                return redirect('shop:cart')
            item.quantity = quantity
            item.save()
            message = 'Panier mis à jour'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'cart_count': cart.total_items,
                'cart_total': float(cart.total),
                'message': message
            })
        
        messages.info(request, message)
        return redirect('shop:cart')
    
    return redirect('shop:cart')


def remove_from_cart(request, item_id):
    """Supprimer du panier"""
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    product_name = item.product.name
    item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True, 
            'cart_count': cart.total_items,
            'cart_total': float(cart.total),
            'message': f'{product_name} supprimé'
        })
    
    messages.info(request, f'{product_name} supprimé du panier')
    return redirect('shop:cart')


def mini_cart(request):
    """Vue AJAX pour le contenu du mini-panier (offcanvas)"""
    cart = get_or_create_cart(request)
    subtotal = cart.total
    
    from core.models import SiteSettings
    site_settings = SiteSettings.get_settings()
    free_shipping_threshold = site_settings.free_shipping_threshold
    
    remaining = max(0, free_shipping_threshold - subtotal) if free_shipping_threshold else 0
    
    return render(request, 'shop/includes/mini_cart_content.html', {
        'cart': cart,
        'cart_count': cart.total_items,
        'subtotal': subtotal,
        'free_shipping_threshold': free_shipping_threshold,
        'remaining_for_free_shipping': remaining,
    })


@login_required
def checkout(request):
    """Page de commande"""
    cart = get_or_create_cart(request)
    
    if cart.total_items == 0:
        messages.warning(request, 'Votre panier est vide')
        return redirect('shop:cart')
    
    subtotal = cart.subtotal
    shipping = 0 if subtotal >= settings.FREE_SHIPPING_THRESHOLD else settings.SHIPPING_COST
    tax = subtotal * (settings.TAX_RATE / 100)
    total = subtotal + shipping + tax
    
    if request.method == 'POST':
        # Créer la commande
        from invoicing.models import Order, OrderItem
        
        order = Order.objects.create(
            user=request.user,
            subtotal=subtotal,
            tax_amount=tax,
            shipping_amount=shipping,
            total=total,
            shipping_address=request.POST.get('shipping_address', ''),
            billing_address=request.POST.get('billing_address', ''),
            notes=request.POST.get('notes', ''),
        )
        
        # Créer les articles de commande
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                product_sku=item.product.sku,
                quantity=item.quantity,
                unit_price=item.product.price,
                total_price=item.total_price,
            )
            
            # Décrémenter le stock
            if item.product.track_stock:
                from .models import StockMovement
                StockMovement.objects.create(
                    product=item.product,
                    movement_type='out',
                    quantity=item.quantity,
                    reason=f'Commande #{order.order_number}',
                )
        
        # Vider le panier
        cart.items.all().delete()
        
        messages.success(request, f'Commande #{order.order_number} créée avec succès!')
        return redirect('invoicing:order_detail', order_id=order.id)
    
    context = {
        'cart': cart,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
    }
    return render(request, 'shop/checkout.html', context)


# ============================================
# INSCRIPTION ET PROFIL UTILISATEUR
# ============================================

def register(request):
    """Inscription d'un nouvel utilisateur"""
    if request.user.is_authenticated:
        return redirect('shop:home')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Créer le profil client
            Customer.objects.create(user=user)
            # Connecter automatiquement
            login(request, user)
            messages.success(request, f'Bienvenue {user.first_name} ! Votre compte a été créé.')
            return redirect('shop:home')
    else:
        form = UserRegisterForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    """Profil utilisateur"""
    # Créer le profil client s'il n'existe pas
    customer, created = Customer.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = CustomerProfileForm(request.POST, instance=customer)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Votre profil a été mis à jour.')
            return redirect('shop:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = CustomerProfileForm(instance=customer)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'shop/profile.html', context)


# ============================================
# PAGES STATIQUES (redirigent vers core)
# ============================================

def contact(request):
    """Page de contact - Redirige vers core"""
    from django.shortcuts import redirect
    return redirect('core:contact')


def about(request):
    """Page À propos - Redirige vers core"""
    from django.shortcuts import redirect
    return redirect('core:about')


def cgv(request):
    """Conditions Générales de Vente - Redirige vers la page dynamique"""
    from core.models import LegalPage
    page = LegalPage.objects.filter(page_type='cgv', is_active=True).first()
    if page:
        return redirect(page.get_absolute_url())
    # Fallback vers template statique si pas de page créée
    return render(request, 'shop/cgv.html')


def legal(request):
    """Mentions légales - Redirige vers la page dynamique"""
    from core.models import LegalPage
    page = LegalPage.objects.filter(page_type='legal', is_active=True).first()
    if page:
        return redirect(page.get_absolute_url())
    # Fallback vers template statique si pas de page créée
    return render(request, 'shop/legal.html')


# ==============================================
# AVIS PRODUITS
# ==============================================

@login_required
def add_review(request, product_id):
    """Ajouter un avis sur un produit"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Vérifier si l'utilisateur a déjà laissé un avis
    if ProductReview.objects.filter(product=product, user=request.user).exists():
        messages.warning(request, _("You have already reviewed this product"))
        return redirect('shop:product_detail', slug=product.slug)
    
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            # Vérifier si achat vérifié
            is_verified = Order.objects.filter(
                user=request.user,
                items__product=product,
                status__in=['delivered', 'shipped']
            ).exists()
            
            ProductReview.objects.create(
                product=product,
                user=request.user,
                rating=int(form.cleaned_data['rating']),
                title=form.cleaned_data['title'],
                comment=form.cleaned_data['comment'],
                is_verified_purchase=is_verified,
                is_approved=False  # Modération manuelle
            )
            messages.success(request, _("Your review has been submitted and is pending approval"))
            return redirect('shop:product_detail', slug=product.slug)
    
    return redirect('shop:product_detail', slug=product.slug)


@login_required
def vote_review_helpful(request, review_id):
    """Voter qu'un avis est utile"""
    if request.method == 'POST':
        review = get_object_or_404(ProductReview, id=review_id, is_approved=True)
        review.helpful_votes += 1
        review.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'votes': review.helpful_votes})
        
        return redirect('shop:product_detail', slug=review.product.slug)
    
    return redirect('shop:home')


# ==============================================
# WISHLIST / FAVORIS
# ==============================================

@login_required
def wishlist_view(request):
    """Afficher la liste de souhaits"""
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    products = wishlist.products.filter(is_active=True)
    
    return render(request, 'shop/wishlist.html', {
        'wishlist': wishlist,
        'products': products,
    })


@login_required
def add_to_wishlist(request, product_id):
    """Ajouter un produit à la wishlist"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    if product in wishlist.products.all():
        wishlist.products.remove(product)
        message = _("Removed from wishlist")
        added = False
    else:
        wishlist.products.add(product)
        message = _("Added to wishlist")
        added = True
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'added': added,
            'count': wishlist.count,
            'message': message
        })
    
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'shop:home'))


@login_required
def remove_from_wishlist(request, product_id):
    """Retirer un produit de la wishlist"""
    product = get_object_or_404(Product, id=product_id)
    
    try:
        wishlist = request.user.wishlist
        wishlist.products.remove(product)
        messages.info(request, _("Removed from wishlist"))
    except Wishlist.DoesNotExist:
        pass
    
    return redirect('shop:wishlist')


@login_required  
def move_wishlist_to_cart(request, product_id):
    """Déplacer un produit de la wishlist vers le panier"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Ajouter au panier
    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    # Retirer de la wishlist
    try:
        wishlist = request.user.wishlist
        wishlist.products.remove(product)
    except Wishlist.DoesNotExist:
        pass
    
    messages.success(request, f'{product.name} ' + _("added to cart"))
    return redirect('shop:wishlist')


# ==============================================
# RECHERCHE AVANCÉE
# ==============================================

def advanced_search(request):
    """Recherche avancée avec filtres"""
    form = AdvancedSearchForm(request.GET)
    products = Product.objects.filter(is_active=True)
    
    if form.is_valid():
        # Mots-clés
        q = form.cleaned_data.get('q')
        if q:
            products = products.filter(
                Q(name__icontains=q) | 
                Q(description__icontains=q) |
                Q(short_description__icontains=q) |
                Q(sku__icontains=q)
            )
        
        # Catégorie
        category = form.cleaned_data.get('category')
        if category:
            products = products.filter(category_id=category)
        
        # Prix minimum
        min_price = form.cleaned_data.get('min_price')
        if min_price:
            products = products.filter(price__gte=min_price)
        
        # Prix maximum
        max_price = form.cleaned_data.get('max_price')
        if max_price:
            products = products.filter(price__lte=max_price)
        
        # En stock uniquement
        in_stock = form.cleaned_data.get('in_stock')
        if in_stock:
            products = products.filter(stock_quantity__gt=0)
        
        # En promotion
        on_sale = form.cleaned_data.get('on_sale')
        if on_sale:
            products = products.filter(compare_at_price__isnull=False).filter(
                compare_at_price__gt=F('price')
            )
        
        # Note minimum
        min_rating = form.cleaned_data.get('min_rating')
        if min_rating:
            products = products.annotate(
                avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
            ).filter(avg_rating__gte=int(min_rating))
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    products_page = paginator.get_page(page)
    
    return render(request, 'shop/advanced_search.html', {
        'form': form,
        'products': products_page,
        'result_count': paginator.count,
    })


# ==============================================
# CHANGEMENT DE LANGUE
# ==============================================

def set_language(request):
    """Changer la langue de l'interface"""
    from django.utils import translation
    from django.conf import settings
    
    lang = request.GET.get('lang', 'fr')
    
    if lang in [l[0] for l in settings.LANGUAGES]:
        translation.activate(lang)
        response = redirect(request.META.get('HTTP_REFERER', 'shop:home'))
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
        return response
    
    return redirect('shop:home')

