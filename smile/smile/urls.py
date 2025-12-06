"""
URL configuration for Smile E-commerce
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.http import JsonResponse

# Dashboard Analytics
from shop.dashboard import dashboard as admin_dashboard


def health_check(request):
    """
    Healthcheck endpoint pour Render.com
    Vérifie que l'application répond correctement
    """
    return JsonResponse({'status': 'healthy', 'app': 'Smile Shop'})


urlpatterns = [
    # Healthcheck pour Render
    path('health/', health_check, name='health_check'),
    
    # Dashboard Analytics (avant admin pour éviter conflit)
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    
    # Admin Django (Facturation & Gestion Stock)
    path('admin/', admin.site.urls),
    
    # Boutique publique
    path('', include('shop.urls')),
    
    # Pages du site (contact, about, légales)
    path('', include('core.urls')),
    
    # Facturation (vues publiques pour clients)
    path('invoices/', include('invoicing.urls')),
    
    # Authentification
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Changement de langue
    path('i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Personnalisation Admin
admin.site.site_header = '🛒 Smile Shop - Administration'
admin.site.site_title = 'Smile Admin'
admin.site.index_title = 'Gestion de la boutique'
