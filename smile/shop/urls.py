from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    
    # Panier
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<uuid:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/mini/', views.mini_cart, name='mini_cart'),
    
    # Commande
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<uuid:order_id>/', views.order_success, name='order_success'),
    
    # Compte utilisateur
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    
    # Avis produits
    path('product/<uuid:product_id>/review/', views.add_review, name='add_review'),
    path('review/<uuid:review_id>/helpful/', views.vote_review_helpful, name='vote_helpful'),
    
    # Wishlist / Favoris
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<uuid:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<uuid:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/move-to-cart/<uuid:product_id>/', views.move_wishlist_to_cart, name='wishlist_to_cart'),
    
    # Recherche avancée
    path('search/', views.advanced_search, name='advanced_search'),
    
    # Changement de langue
    path('set-language/', views.set_language, name='set_language'),
]
