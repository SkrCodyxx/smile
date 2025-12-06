#!/bin/bash
# ==============================================================================
# SCRIPT DE RÉINITIALISATION DU MOT DE PASSE ADMINISTRATEUR
# Smile E-commerce - PythonAnywhere
# ==============================================================================

echo "=============================================="
echo "🔐 RÉINITIALISATION MOT DE PASSE ADMIN"
echo "=============================================="
echo ""

# Activer l'environnement virtuel
source /home/smile/.virtualenvs/smileenv/bin/activate

# Se déplacer dans le répertoire du projet
cd /home/smile/smile/smile

echo "📧 Recherche de l'utilisateur admin existant..."
echo ""

# Lister les superusers existants
python manage.py shell --settings=smile.settings_pythonanywhere << 'EOF'
from django.contrib.auth.models import User

print("=" * 50)
print("UTILISATEURS ADMINISTRATEURS EXISTANTS:")
print("=" * 50)

superusers = User.objects.filter(is_superuser=True)
if superusers.exists():
    for user in superusers:
        print(f"  📧 Email: {user.email}")
        print(f"  👤 Username: {user.username}")
        print(f"  ✅ Actif: {user.is_active}")
        print("-" * 30)
else:
    print("  ❌ Aucun superuser trouvé!")
    print("  Création d'un nouveau superuser nécessaire.")

print("")
EOF

echo ""
echo "=============================================="
echo "Que voulez-vous faire?"
echo "=============================================="
echo ""
echo "1. Réinitialiser le mot de passe d'un admin existant"
echo "2. Créer un nouveau superuser"
echo "3. Lister tous les utilisateurs"
echo ""
read -p "Votre choix (1/2/3): " choice

case $choice in
    1)
        echo ""
        read -p "📧 Email ou username de l'admin: " admin_id
        read -s -p "🔑 Nouveau mot de passe: " new_pass
        echo ""
        read -s -p "🔑 Confirmer le mot de passe: " confirm_pass
        echo ""
        
        if [ "$new_pass" != "$confirm_pass" ]; then
            echo "❌ Les mots de passe ne correspondent pas!"
            exit 1
        fi
        
        python manage.py shell --settings=smile.settings_pythonanywhere << EOF
from django.contrib.auth.models import User

try:
    # Chercher par email ou username
    user = User.objects.filter(email='$admin_id').first() or User.objects.filter(username='$admin_id').first()
    
    if user:
        user.set_password('$new_pass')
        user.save()
        print(f"✅ Mot de passe réinitialisé pour: {user.username} ({user.email})")
        print("")
        print("📝 Informations de connexion:")
        print(f"   URL: https://smile.pythonanywhere.com/admin/")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
    else:
        print(f"❌ Utilisateur '{$admin_id}' non trouvé!")
except Exception as e:
    print(f"❌ Erreur: {e}")
EOF
        ;;
        
    2)
        echo ""
        echo "Création d'un nouveau superuser..."
        python manage.py createsuperuser --settings=smile.settings_pythonanywhere
        ;;
        
    3)
        echo ""
        python manage.py shell --settings=smile.settings_pythonanywhere << 'EOF'
from django.contrib.auth.models import User

print("=" * 60)
print("TOUS LES UTILISATEURS:")
print("=" * 60)

for user in User.objects.all()[:20]:
    status = "🔑 Admin" if user.is_superuser else "👤 User"
    active = "✅" if user.is_active else "❌"
    print(f"{active} {status} | {user.username} | {user.email}")

total = User.objects.count()
print("-" * 60)
print(f"Total: {total} utilisateurs")
EOF
        ;;
        
    *)
        echo "Choix invalide"
        exit 1
        ;;
esac

echo ""
echo "=============================================="
echo "✅ Opération terminée!"
echo "=============================================="
