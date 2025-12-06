#!/bin/bash
# =============================================================================
# SCRIPT DE DÉPLOIEMENT AUTOMATIQUE - Smile Shop
# =============================================================================
# Usage: bash setup_pythonanywhere.sh
# =============================================================================

set -e  # Arrête le script en cas d'erreur

echo "🚀 Déploiement automatique de Smile Shop sur PythonAnywhere"
echo "============================================================"

# Variables
PROJECT_DIR="$HOME/smile/smile"
VENV_NAME="smileenv"
SETTINGS="smile.settings_pythonanywhere"

# Activer l'environnement virtuel
echo ""
echo "📦 Activation de l'environnement virtuel..."
source $HOME/.virtualenvs/$VENV_NAME/bin/activate

# Aller dans le dossier du projet
cd $PROJECT_DIR

# Mettre à jour depuis GitHub
echo ""
echo "📥 Mise à jour depuis GitHub..."
cd $HOME/smile
git pull
cd $PROJECT_DIR

# Installer les dépendances
echo ""
echo "📦 Installation des dépendances..."
pip install -r requirements.txt -q

# Migrations
echo ""
echo "🗄️ Application des migrations..."
python manage.py migrate --settings=$SETTINGS

# Fichiers statiques
echo ""
echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --settings=$SETTINGS

# Compiler les traductions
echo ""
echo "🌐 Compilation des traductions..."
python manage.py compilemessages --settings=$SETTINGS 2>/dev/null || echo "⚠️ Pas de traductions à compiler"

# Créer les données initiales
echo ""
echo "🌍 Création des données initiales..."
python manage.py shell --settings=$SETTINGS << 'PYTHON'
from core.models import Language, Currency

# Langues
for code, name, default in [('fr', 'Français', True), ('en', 'English', False), ('ht', 'Kreyòl Ayisyen', False)]:
    obj, created = Language.objects.get_or_create(code=code, defaults={'name': name, 'is_active': True, 'is_default': default})
    if created:
        print(f"✅ Langue créée: {name}")
    else:
        print(f"ℹ️ Langue existante: {name}")

# Devises
for code, name, symbol, rate, default in [('EUR', 'Euro', '€', 1.0, True), ('USD', 'Dollar US', '$', 1.09, False), ('CAD', 'Dollar Canadien', 'CA$', 1.49, False), ('HTG', 'Gourde Haïtienne', 'G', 143.50, False)]:
    obj, created = Currency.objects.get_or_create(code=code, defaults={'name': name, 'symbol': symbol, 'rate': rate, 'is_active': True, 'is_default': default})
    if created:
        print(f"✅ Devise créée: {name}")
    else:
        print(f"ℹ️ Devise existante: {name}")

print("")
print("🎉 Données initiales configurées!")
PYTHON

echo ""
echo "============================================================"
echo "✅ DÉPLOIEMENT TERMINÉ !"
echo "============================================================"
echo ""
echo "📋 Prochaines étapes (une seule fois) :"
echo ""
echo "1. Créer un superuser (si pas encore fait) :"
echo "   python manage.py createsuperuser --settings=$SETTINGS"
echo ""
echo "2. Configurer l'app Web dans PythonAnywhere :"
echo "   - Source code: /home/smile/smile/smile"
echo "   - Virtualenv: /home/smile/.virtualenvs/smileenv"
echo "   - Static files: /static/ -> /home/smile/smile/smile/staticfiles"
echo "   - Static files: /media/ -> /home/smile/smile/smile/media"
echo ""
echo "3. Éditer le fichier WSGI (voir wsgi_pythonanywhere.py)"
echo ""
echo "4. Cliquer 'Reload' dans l'onglet Web"
echo ""
echo "🌐 Ton site: https://smile.pythonanywhere.com"
echo ""
