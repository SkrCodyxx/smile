"""
URLs pour l'application core
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Pages légales dynamiques
    path('page/<slug:slug>/', views.legal_page, name='legal_page'),
    
    # Page de contact
    path('contact/', views.contact_page, name='contact'),
    
    # À propos
    path('about/', views.about_page, name='about'),
    
    # Conditions Générales de Vente
    path('cgv/', views.cgv_page, name='cgv'),
    
    # Mentions légales
    path('legal/', views.legal_page_static, name='legal'),
    
    # Politique de confidentialité
    path('privacy/', views.privacy_page, name='privacy'),
    
    # FAQ
    path('faq/', views.faq_page, name='faq'),
    
    # Livraison
    path('shipping/', views.shipping_page, name='shipping'),
    
    # Retours
    path('returns/', views.returns_page, name='returns'),
    
    # Changement de devise
    path('set-currency/', views.set_currency, name='set_currency'),
]
