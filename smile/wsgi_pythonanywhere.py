"""
WSGI config for Smile E-commerce on PythonAnywhere
===================================================
Copie ce contenu dans l'onglet "Web" → "WSGI configuration file"
"""
import os
import sys

# =============================================================================
# CONFIGURATION - MODIFIE CES VALEURS
# =============================================================================
# Remplace 'TONUSERNAME' par ton nom d'utilisateur PythonAnywhere
USERNAME = 'TONUSERNAME'

# Chemin vers ton projet (normalement /home/TONUSERNAME/smile)
PROJECT_PATH = f'/home/{USERNAME}/smile'

# =============================================================================
# NE PAS MODIFIER CI-DESSOUS
# =============================================================================

# Ajouter le projet au path Python
if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)

# Variables d'environnement
os.environ['DJANGO_SETTINGS_MODULE'] = 'smile.settings_pythonanywhere'

# Optionnel: ajouter ta clé secrète ici (ou dans l'onglet "Files" → .env)
# os.environ['SECRET_KEY'] = 'ta-cle-secrete-ici'
# os.environ['DB_PASSWORD'] = 'ton-mot-de-passe-mysql'

# Charger l'application Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
