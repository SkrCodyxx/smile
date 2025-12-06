#!/usr/bin/env bash
# =============================================================================
# BUILD SCRIPT POUR RENDER.COM - Smile E-commerce
# =============================================================================
# Ce script est exécuté par Render lors du déploiement
# Il configure la base de données et prépare l'application
# =============================================================================

set -o errexit  # Exit on error

echo "🚀 Démarrage du build Smile E-commerce..."

# Installation des dépendances Python
echo "📦 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Compilation des traductions
echo "🌐 Compilation des traductions..."
python manage.py compilemessages || echo "⚠️ Pas de traductions à compiler"

# Collecte des fichiers statiques
echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# Migrations de la base de données
echo "🗄️ Exécution des migrations..."
python manage.py migrate --noinput

# Création du superuser si les variables sont définies
if [[ -n "$DJANGO_SUPERUSER_USERNAME" ]] && [[ -n "$DJANGO_SUPERUSER_EMAIL" ]] && [[ -n "$DJANGO_SUPERUSER_PASSWORD" ]]; then
    echo "👤 Création du superuser..."
    python manage.py createsuperuser --noinput || echo "⚠️ Superuser existe déjà"
fi

# Création des données initiales (langues, devises, etc.)
echo "🌍 Initialisation des données..."
python manage.py shell << 'EOF'
from core.models import Language, Currency

# Création des langues si elles n'existent pas
languages_data = [
    {'code': 'fr', 'name': 'Français', 'is_active': True, 'is_default': True},
    {'code': 'en', 'name': 'English', 'is_active': True, 'is_default': False},
    {'code': 'ht', 'name': 'Kreyòl Ayisyen', 'is_active': True, 'is_default': False},
]

for lang_data in languages_data:
    lang, created = Language.objects.get_or_create(
        code=lang_data['code'],
        defaults={'name': lang_data['name'], 'is_active': lang_data['is_active'], 'is_default': lang_data['is_default']}
    )
    if created:
        print(f"✅ Langue créée: {lang.name}")
    else:
        print(f"ℹ️ Langue existante: {lang.name}")

# Création des devises si elles n'existent pas
currencies_data = [
    {'code': 'EUR', 'name': 'Euro', 'symbol': '€', 'rate': 1.0, 'is_active': True, 'is_default': True},
    {'code': 'USD', 'name': 'Dollar US', 'symbol': '$', 'rate': 1.09, 'is_active': True, 'is_default': False},
    {'code': 'CAD', 'name': 'Dollar Canadien', 'symbol': 'CA$', 'rate': 1.49, 'is_active': True, 'is_default': False},
    {'code': 'HTG', 'name': 'Gourde Haïtienne', 'symbol': 'G', 'rate': 143.50, 'is_active': True, 'is_default': False},
]

for curr_data in currencies_data:
    curr, created = Currency.objects.get_or_create(
        code=curr_data['code'],
        defaults={
            'name': curr_data['name'], 
            'symbol': curr_data['symbol'], 
            'rate': curr_data['rate'],
            'is_active': curr_data['is_active'], 
            'is_default': curr_data['is_default']
        }
    )
    if created:
        print(f"✅ Devise créée: {curr.name}")
    else:
        print(f"ℹ️ Devise existante: {curr.name}")

print("✅ Données initiales configurées!")
EOF

echo "✅ Build terminé avec succès!"
