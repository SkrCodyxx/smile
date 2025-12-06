"""
Django settings for Smile E-commerce - PYTHONANYWHERE
=====================================================
Configuration optimisée pour PythonAnywhere (plan gratuit)
"""
import os
from pathlib import Path

# Import des settings de base
from .settings import *

# =============================================================================
# SÉCURITÉ PRODUCTION
# =============================================================================
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-pythonanywhere-env')

# Remplace 'TONUSERNAME' par ton nom d'utilisateur PythonAnywhere
ALLOWED_HOSTS = [
    '.pythonanywhere.com',
    'localhost',
    '127.0.0.1',
]

# Sécurité
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# =============================================================================
# BASE DE DONNÉES - MySQL (gratuit sur PythonAnywhere)
# =============================================================================
# Format: TONUSERNAME$smile_db
# Va dans l'onglet "Databases" sur PythonAnywhere pour créer ta DB

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'TONUSERNAME$smile_db'),
        'USER': os.environ.get('DB_USER', 'TONUSERNAME'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),  # Ton mot de passe MySQL
        'HOST': os.environ.get('DB_HOST', 'TONUSERNAME.mysql.pythonanywhere-services.com'),
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

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
# PythonAnywhere sert les fichiers statiques directement

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Désactiver WhiteNoise (PythonAnywhere gère les statiques)
MIDDLEWARE = [m for m in MIDDLEWARE if 'whitenoise' not in m.lower()]
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# =============================================================================
# LOGGING
# =============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'error.log',
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
    'https://*.pythonanywhere.com',
]

# =============================================================================
# CRON - Désactivé (utiliser les tâches planifiées PythonAnywhere)
# =============================================================================
CRONJOBS = []

# =============================================================================
# EMAIL - Console pour le plan gratuit
# =============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
