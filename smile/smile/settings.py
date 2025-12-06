"""
Django settings for Smile E-commerce
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Third party
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    'django_crontab',
    # Nos apps
    'core',  # Configuration du site
    'shop',
    'invoicing',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Multi-langues
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'smile.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',  # Multi-langues
                'shop.context_processors.cart_context',
                'shop.context_processors.categories_context',
                'shop.context_processors.wishlist_context',
                'core.context_processors.site_settings',  # Config dynamique du site
            ],
        },
    },
]

WSGI_APPLICATION = 'smile.wsgi.application'

# Database
if os.environ.get('DATABASE_URL'):
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'smile_db'),
            'USER': os.environ.get('DB_USER', 'smile_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'smile_password_2024'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }

# Cache avec Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Multi-langues (Français, English, Kreyòl Ayisyen)
from django.utils.translation import gettext_lazy as _

LANGUAGES = [
    ('fr', _('Français')),
    ('en', _('English')),
    ('ht', _('Kreyòl Ayisyen')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Login
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'shop:home'
LOGOUT_REDIRECT_URL = 'shop:home'

# Shop settings
SHOP_NAME = 'Smile Shop'
SHOP_EMAIL = 'contact@smile-shop.com'
SHOP_PHONE = '+33 1 23 45 67 89'
SHOP_ADDRESS = '123 Rue du Commerce, 75001 Paris'
TAX_RATE = 20  # TVA en %
CURRENCY = 'EUR'
CURRENCY_SYMBOL = '€'
FREE_SHIPPING_THRESHOLD = 50
SHIPPING_COST = 5.99

# =============================================================================
# TÂCHES CRON - Mise à jour automatique des taux de change
# =============================================================================
# Format: (minute, heure, jour_du_mois, mois, jour_semaine)
# La BCE publie les taux vers 16h CET, on met à jour à 17h
CRONJOBS = [
    # Mise à jour des taux de change chaque jour à 17h00
    ('0 17 * * *', 'core.cron.update_exchange_rates_job', '>> /var/log/cron_exchange_rates.log 2>&1'),
    
    # Backup option: mise à jour aussi à 8h00 au cas où
    ('0 8 * * *', 'core.cron.update_exchange_rates_job', '>> /var/log/cron_exchange_rates.log 2>&1'),
]

# Clé API pour les services de taux de change (optionnel)
# Frankfurter est gratuit et illimité, pas besoin de clé
EXCHANGE_RATE_API_KEY = os.environ.get('EXCHANGE_RATE_API_KEY', None)
