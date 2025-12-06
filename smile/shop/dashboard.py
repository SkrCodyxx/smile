"""
Dashboard Analytics pour Smile Shop Admin
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from shop.models import Product, Category, ProductReview, Wishlist, Cart
from invoicing.models import Order, Invoice, Customer


@staff_member_required
def dashboard(request):
    """Vue du tableau de bord analytics"""
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)
    
    # ============================================
    # MÉTRIQUES PRINCIPALES
    # ============================================
    
    # Chiffre d'affaires
    revenue_today = Order.objects.filter(
        created_at__date=today, 
        payment_status='paid'
    ).aggregate(total=Sum('total'))['total'] or Decimal('0')
    
    revenue_month = Order.objects.filter(
        created_at__date__gte=start_of_month,
        payment_status='paid'
    ).aggregate(total=Sum('total'))['total'] or Decimal('0')
    
    revenue_30_days = Order.objects.filter(
        created_at__date__gte=last_30_days,
        payment_status='paid'
    ).aggregate(total=Sum('total'))['total'] or Decimal('0')
    
    # Commandes
    orders_today = Order.objects.filter(created_at__date=today).count()
    orders_month = Order.objects.filter(created_at__date__gte=start_of_month).count()
    orders_pending = Order.objects.filter(status='pending').count()
    orders_processing = Order.objects.filter(status__in=['confirmed', 'processing']).count()
    
    # Panier moyen
    avg_order = Order.objects.filter(
        created_at__date__gte=last_30_days,
        payment_status='paid'
    ).aggregate(avg=Avg('total'))['avg'] or Decimal('0')
    
    # Clients
    new_customers_month = Customer.objects.filter(
        created_at__date__gte=start_of_month
    ).count()
    total_customers = Customer.objects.count()
    
    # ============================================
    # STOCK
    # ============================================
    
    products_low_stock = Product.objects.filter(
        is_active=True,
        track_stock=True,
        stock_quantity__lte=F('low_stock_threshold')
    ).exclude(stock_quantity=0)
    
    products_out_of_stock = Product.objects.filter(
        is_active=True,
        track_stock=True,
        stock_quantity=0
    )
    
    # ============================================
    # PRODUITS
    # ============================================
    
    total_products = Product.objects.filter(is_active=True).count()
    total_categories = Category.objects.filter(is_active=True).count()
    
    # Produits les plus vendus (30 derniers jours)
    from invoicing.models import OrderItem
    top_products = OrderItem.objects.filter(
        order__created_at__date__gte=last_30_days,
        order__payment_status='paid'
    ).values('product__name', 'product__id', 'product__image').annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('total_price')
    ).order_by('-total_sold')[:5]
    
    # Catégories populaires
    top_categories = Category.objects.filter(is_active=True).annotate(
        product_count=Count('products', filter=F('products__is_active'))
    ).order_by('-product_count')[:5]
    
    # ============================================
    # AVIS
    # ============================================
    
    reviews_pending = ProductReview.objects.filter(is_approved=False).count()
    reviews_total = ProductReview.objects.count()
    avg_rating = ProductReview.objects.filter(is_approved=True).aggregate(
        avg=Avg('rating')
    )['avg'] or 0
    
    # ============================================
    # GRAPHIQUES (données pour les 30 derniers jours)
    # ============================================
    
    # Ventes par jour
    sales_by_day = Order.objects.filter(
        created_at__date__gte=last_30_days,
        payment_status='paid'
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total=Sum('total'),
        count=Count('id')
    ).order_by('date')
    
    # Transformer en listes pour JavaScript
    chart_labels = [item['date'].strftime('%d/%m') for item in sales_by_day]
    chart_revenue = [float(item['total']) for item in sales_by_day]
    chart_orders = [item['count'] for item in sales_by_day]
    
    # ============================================
    # FACTURES
    # ============================================
    
    invoices_unpaid = Invoice.objects.filter(status__in=['draft', 'sent']).count()
    invoices_total_unpaid = Invoice.objects.filter(
        status__in=['draft', 'sent']
    ).aggregate(total=Sum('total'))['total'] or Decimal('0')
    
    # ============================================
    # ACTIVITÉ RÉCENTE
    # ============================================
    
    recent_orders = Order.objects.order_by('-created_at')[:5]
    recent_reviews = ProductReview.objects.order_by('-created_at')[:5]
    
    # Paniers abandonnés (plus de 24h)
    abandoned_carts = Cart.objects.filter(
        updated_at__lt=timezone.now() - timedelta(hours=24)
    ).exclude(items=None).count()
    
    context = {
        # Métriques principales
        'revenue_today': revenue_today,
        'revenue_month': revenue_month,
        'revenue_30_days': revenue_30_days,
        'orders_today': orders_today,
        'orders_month': orders_month,
        'orders_pending': orders_pending,
        'orders_processing': orders_processing,
        'avg_order': avg_order,
        'new_customers_month': new_customers_month,
        'total_customers': total_customers,
        
        # Stock
        'products_low_stock': products_low_stock,
        'products_low_stock_count': products_low_stock.count(),
        'products_out_of_stock': products_out_of_stock,
        'products_out_of_stock_count': products_out_of_stock.count(),
        
        # Produits
        'total_products': total_products,
        'total_categories': total_categories,
        'top_products': top_products,
        'top_categories': top_categories,
        
        # Avis
        'reviews_pending': reviews_pending,
        'reviews_total': reviews_total,
        'avg_rating': round(avg_rating, 1),
        
        # Graphiques
        'chart_labels': chart_labels,
        'chart_revenue': chart_revenue,
        'chart_orders': chart_orders,
        
        # Factures
        'invoices_unpaid': invoices_unpaid,
        'invoices_total_unpaid': invoices_total_unpaid,
        
        # Activité récente
        'recent_orders': recent_orders,
        'recent_reviews': recent_reviews,
        'abandoned_carts': abandoned_carts,
    }
    
    return render(request, 'admin/dashboard.html', context)
