"""
Django settings for Smile E-commerce - PRODUCTION (Render.com)
===============================================================
Ce fichier hérite de settings.py et override les paramètres pour la production.
"""
import os
import dj_database_url
from pathlib import Path

# Import des settings de base
from .settings import *

# =============================================================================
# SÉCURITÉ PRODUCTION
# =============================================================================
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')

# Hosts autorisés - Render utilise .onrender.com
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '.onrender.com').split(',')

# Sécurité HTTPS (Render gère SSL automatiquement)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS - Force HTTPS pendant 1 an
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# =============================================================================
# BASE DE DONNÉES - PostgreSQL sur Render
# =============================================================================
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }

# =============================================================================
# CACHE - Désactivé sur le plan gratuit (pas de Redis)
# =============================================================================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Sessions via base de données (pas de Redis sur plan gratuit)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# =============================================================================
# FICHIERS STATIQUES - WhiteNoise
# =============================================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# WhiteNoise sert aussi les fichiers media en production
# Note: Pour un vrai site e-commerce, utilisez un CDN comme Cloudinary
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =============================================================================
# LOGGING
# =============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

# =============================================================================
# EMAIL - Configuration pour production
# =============================================================================
# À configurer avec un service comme SendGrid, Mailgun, etc.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.sendgrid.net')
# EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'apikey')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
# DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@smile-shop.com')

# =============================================================================
# CSRF - Trusts pour Render
# =============================================================================
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
]

# Ajout de domaines personnalisés si configurés
CUSTOM_DOMAIN = os.environ.get('CUSTOM_DOMAIN')
if CUSTOM_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f'https://{CUSTOM_DOMAIN}')
    ALLOWED_HOSTS.append(CUSTOM_DOMAIN)

# =============================================================================
# CRON - Désactivé sur Render (utiliser Render Cron Jobs à la place)
# =============================================================================
CRONJOBS = []
