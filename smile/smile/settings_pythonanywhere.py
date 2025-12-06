
"""
================================================================================
SMILE E-COMMERCE - CONFIGURATION PRODUCTION PYTHONANYWHERE
================================================================================
Site: https://smile.pythonanywhere.com
Plan: Gratuit (MySQL + 512MB storage)
Dernière mise à jour: Décembre 2025
================================================================================
"""
import os
from pathlib import Path

# Import des settings de base (apps, templates, etc.)
from .settings import *


# ==============================================================================
# 1. INFORMATIONS DU SITE
# ==============================================================================
SITE_NAME = 'Smile Shop'
SITE_URL = 'https://smile.pythonanywhere.com'
SITE_DESCRIPTION = 'Votre boutique en ligne de confiance'


# ==============================================================================
# 2. MODE PRODUCTION
# ==============================================================================
DEBUG = False
SECRET_KEY = 'sm1l3-sh0p-s3cr3t-k3y-2024-pr0duct10n-x7k9m2p4-secure'

ALLOWED_HOSTS = [
    'smile.pythonanywhere.com',
    'www.smile.pythonanywhere.com',
]


# ==============================================================================
# 3. BASE DE DONNÉES - MySQL PythonAnywhere
# ==============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'smile$smiledb',
        'USER': 'smile',
        'PASSWORD': 'Sm!le2000Sm!',
        'HOST': 'smile.mysql.pythonanywhere-services.com',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}


# ==============================================================================
# 4. EMAIL - Gmail SMTP
# ==============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'smileinc2000@gmail.com'
EMAIL_HOST_PASSWORD = 'acojpbjchsbltcgm'
DEFAULT_FROM_EMAIL = 'Smile Shop <smileinc2000@gmail.com>'
SERVER_EMAIL = 'smileinc2000@gmail.com'

# Admin qui reçoit les erreurs et notifications
ADMINS = [
    ('Admin Smile', 'smileinc2000@gmail.com'),
]
MANAGERS = ADMINS


# ==============================================================================
# 5. WHATSAPP BUSINESS
# ==============================================================================
WHATSAPP_BUSINESS_NUMBER = '50937773508'  # Format: code pays + numéro


# ==============================================================================
# 5b. PAIEMENT MOBILE - MonCash & NatCash
# ==============================================================================
# TODO: Remplacez par vos vrais numéros
MONCASH_NUMBER = '37773508'  # Votre numéro MonCash (sans code pays)
NATCASH_NUMBER = '37773508'  # Votre numéro NatCash (sans code pays)
MONCASH_NAME = 'SMILE SHOP'  # Nom affiché sur MonCash
NATCASH_NAME = 'SMILE SHOP'  # Nom affiché sur NatCash


# ==============================================================================
# 6. FICHIERS STATIQUES ET MEDIA
# ==============================================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# PythonAnywhere gère les fichiers statiques, pas besoin de WhiteNoise
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Retirer WhiteNoise du middleware
MIDDLEWARE = [m for m in MIDDLEWARE if 'whitenoise' not in m.lower()]


# ==============================================================================
# 7. SÉCURITÉ HTTPS
# ==============================================================================
# Protection XSS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Cookies sécurisés (HTTPS uniquement)
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# HSTS - Force HTTPS pendant 1 an
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# PythonAnywhere gère le SSL redirect
SECURE_SSL_REDIRECT = False

# Origines CSRF autorisées
CSRF_TRUSTED_ORIGINS = [
    'https://smile.pythonanywhere.com',
]


# ==============================================================================
# 8. CACHE - Mémoire locale (pas de Redis sur plan gratuit)
# ==============================================================================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'smile-cache',
        'TIMEOUT': 300,  # 5 minutes
    }
}


# ==============================================================================
# 9. SESSIONS
# ==============================================================================
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 semaines
SESSION_SAVE_EVERY_REQUEST = True


# ==============================================================================
# 10. LOGGING - Journal des erreurs
# ==============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} | {module} | {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'error.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}


# ==============================================================================
# 11. PARAMÈTRES BOUTIQUE
# ==============================================================================
SHOP_NAME = 'Smile Shop'
SHOP_EMAIL = 'smileinc2000@gmail.com'
SHOP_PHONE = '+509 37 77 35 08'
SHOP_ADDRESS = 'Port-au-Prince, Haïti'
TAX_RATE = 0  # Pas de TVA en Haïti
DEFAULT_CURRENCY = 'HTG'


# ==============================================================================
# 12. INTERNATIONALISATION
# ==============================================================================
LANGUAGE_CODE = 'fr'
TIME_ZONE = 'America/Port-au-Prince'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# ==============================================================================
# FIN DE LA CONFIGURATION
# ==============================================================================
