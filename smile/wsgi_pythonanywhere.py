"""
WSGI config for Smile E-commerce on PythonAnywhere
===================================================
Copie ce contenu dans l'onglet "Web" → "WSGI configuration file"

Username PythonAnywhere: smile
Base de données: Supabase PostgreSQL
"""
import os
import sys

# =============================================================================
# CONFIGURATION POUR smile.pythonanywhere.com
# =============================================================================

# Chemin vers le projet
path = '/home/smile/smile/smile'
if path not in sys.path:
    sys.path.append(path)

# Variables d'environnement
os.environ['DJANGO_SETTINGS_MODULE'] = 'smile.settings_pythonanywhere'
os.environ['SECRET_KEY'] = 'smile-secret-key-2024-production-change-me'
os.environ['DATABASE_URL'] = 'postgresql://postgres.crieerueopsntuhraatj:Sm%21le2000Sm%21@aws-0-eu-central-1.pooler.supabase.com:6543/postgres'

# Application WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
