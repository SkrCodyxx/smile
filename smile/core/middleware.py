"""
Middlewares pour l'application core
"""
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse


class MaintenanceModeMiddleware:
    """
    Middleware pour le mode maintenance
    Bloque l'accès au site sauf pour les admins
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Toujours autoriser l'admin et les fichiers statiques
        if request.path.startswith('/admin') or request.path.startswith('/static'):
            return self.get_response(request)
        
        # Vérifier le mode maintenance
        try:
            from .models import SiteSettings
            settings = SiteSettings.get_settings()
            
            if settings.maintenance_mode:
                # Les staff peuvent toujours accéder
                if request.user.is_authenticated and request.user.is_staff:
                    return self.get_response(request)
                
                # Afficher la page de maintenance
                return render(request, 'core/maintenance.html', {
                    'maintenance_message': settings.maintenance_message,
                }, status=503)
        except:
            pass
        
        return self.get_response(request)
