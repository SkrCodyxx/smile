"""
WSGI config for Smile E-commerce on PythonAnywhere
===================================================
Copie ce contenu dans l'onglet "Web" → "WSGI configuration file"

Username PythonAnywhere: smile
Base de données: MySQL PythonAnywhere - smile$smiledb
"""
import os
import sys

# Chemin vers le projet
path = '/home/smile/smile/smile'
if path not in sys.path:
    sys.path.append(path)

# Variables d'environnement
os.environ['DJANGO_SETTINGS_MODULE'] = 'smile.settings_pythonanywhere'
os.environ['SECRET_KEY'] = 'smile-secret-key-2024-production-change-me'
os.environ['DB_PASSWORD'] = 'Sm!le2000Sm!'

# Application WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
