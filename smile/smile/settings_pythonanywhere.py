"""
Django settings for Smile E-commerce - PYTHONANYWHERE PRODUCTION
================================================================
Configuration pour PythonAnywhere (plan gratuit) avec MySQL
"""
import os
from pathlib import Path

# Import des settings de base
from .settings import *

# =============================================================================
# SÉCURITÉ PRODUCTION
# =============================================================================
DEBUG = False

# SECRET_KEY - IMPORTANT: Définis cette variable dans PythonAnywhere
# Va dans Web > onglet "Web" > section "Environment variables" (ou fichier .env)
SECRET_KEY = os.environ.get('SECRET_KEY', 'sm1l3-sh0p-s3cr3t-k3y-2024-pr0duct10n-x7k9m2p4')

# Username PythonAnywhere: smile
ALLOWED_HOSTS = [
    'smile.pythonanywhere.com',
    '.pythonanywhere.com',
]

# Sécurité renforcée pour production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False  # PythonAnywhere gère HTTPS
SECURE_HSTS_SECONDS = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# =============================================================================
# BASE DE DONNÉES - MySQL PythonAnywhere (GRATUIT)
# =============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'smile$smiledb',
        'USER': 'smile',
        'PASSWORD': os.environ.get('DB_PASSWORD', 'Sm!le2000Sm!'),
        'HOST': 'smile.mysql.pythonanywhere-services.com',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# =============================================================================
# EMAIL - Gmail SMTP (GRATUIT)
# =============================================================================
# Pour utiliser Gmail, tu dois:
# 1. Activer "Accès moins sécurisé" OU créer un "Mot de passe d'application"
# 2. Aller sur: https://myaccount.google.com/apppasswords
# 3. Créer un mot de passe pour "Mail" > "Autre (Smile Shop)"
# 4. Copier le mot de passe de 16 caractères généré

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')  # ton.email@gmail.com
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')  # Mot de passe d'app 16 car
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Smile Shop <noreply@smileshop.com>')
SERVER_EMAIL = EMAIL_HOST_USER

# Si les emails ne fonctionnent pas, utiliser console en fallback
if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# =============================================================================
# WHATSAPP BUSINESS - Configuration
# =============================================================================
# Numéro WhatsApp Business (format international sans +)
# Exemple: 33612345678 pour la France, 50937123456 pour Haïti
WHATSAPP_BUSINESS_NUMBER = os.environ.get('WHATSAPP_NUMBER', '')

# =============================================================================
# CACHE - Local Memory (pas de Redis sur plan gratuit)
# =============================================================================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Sessions via base de données
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# =============================================================================
# FICHIERS STATIQUES
# =============================================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Désactiver WhiteNoise (PythonAnywhere gère les statiques)
MIDDLEWARE = [m for m in MIDDLEWARE if 'whitenoise' not in m.lower()]
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# =============================================================================
# LOGGING - Erreurs en fichier
# =============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
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
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# =============================================================================
# CSRF - Trusts pour PythonAnywhere
# =============================================================================
CSRF_TRUSTED_ORIGINS = [
    'https://smile.pythonanywhere.com',
]

# =============================================================================
# ADMINS - Pour recevoir les erreurs par email
# =============================================================================
ADMINS = [
    ('Admin Smile', os.environ.get('ADMIN_EMAIL', '')),
]

# =============================================================================
# SITE INFO
# =============================================================================
SITE_NAME = 'Smile Shop'
SITE_URL = 'https://smile.pythonanywhere.com'
