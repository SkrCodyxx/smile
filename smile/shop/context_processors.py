from .models import Cart, Category, Wishlist


def cart_context(request):
    """Ajoute le panier au contexte global"""
    cart_count = 0
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.total_items
        except Cart.DoesNotExist:
            pass
    else:
        session_key = request.session.session_key
        if session_key:
            try:
                cart = Cart.objects.get(session_key=session_key)
                cart_count = cart.total_items
            except Cart.DoesNotExist:
                pass
    
    return {'cart_count': cart_count}


def categories_context(request):
    """Ajoute les catégories au contexte global"""
    return {
        'all_categories': Category.objects.filter(is_active=True, parent=None)
    }


def wishlist_context(request):
    """Ajoute la wishlist au contexte global"""
    wishlist_count = 0
    wishlist_products = []
    
    if request.user.is_authenticated:
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            wishlist_count = wishlist.count
            wishlist_products = list(wishlist.products.values_list('id', flat=True))
        except Wishlist.DoesNotExist:
            pass
    
    return {
        'wishlist_count': wishlist_count,
        'wishlist_product_ids': wishlist_products
    }
