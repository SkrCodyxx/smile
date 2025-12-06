# 🚀 Guide de Configuration Production - Smile E-commerce

## 📋 Table des matières

1. [Configuration Gmail SMTP](#-configuration-gmail-smtp)
2. [Configuration WhatsApp Business](#-configuration-whatsapp-business)
3. [Variables d'environnement PythonAnywhere](#-variables-denvironnement-pythonanywhere)
4. [Déploiement sur PythonAnywhere](#-déploiement-sur-pythonanywhere)
5. [Vérification de la configuration](#-vérification-de-la-configuration)
6. [Utilisation des emails dans le code](#-utilisation-des-emails-dans-le-code)
7. [Dépannage](#-dépannage)

---

## 📧 Configuration Gmail SMTP

### Étape 1 : Activer l'authentification à 2 facteurs

1. Connectez-vous à votre compte Gmail
2. Allez sur : https://myaccount.google.com/security
3. Cliquez sur **"Validation en deux étapes"**
4. Suivez les instructions pour activer la validation en deux étapes

### Étape 2 : Créer un mot de passe d'application

1. Allez sur : https://myaccount.google.com/apppasswords
2. Sélectionnez **"Autre (nom personnalisé)"**
3. Entrez : `Smile E-commerce`
4. Cliquez sur **"Générer"**
5. **COPIEZ** le mot de passe de 16 caractères affiché (ex: `abcd efgh ijkl mnop`)
6. **IMPORTANT** : Retirez les espaces → `abcdefghijklmnop`

### Étape 3 : Configurer dans PythonAnywhere

Sur PythonAnywhere, allez dans **Web** > **Files** et éditez le fichier `.env` :

```bash
# Dans /home/smile/.env
DJANGO_SECRET_KEY=votre_secret_key_generee
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
WHATSAPP_NUMBER=50937773508
```

**OU** configurez les variables d'environnement dans le fichier WSGI.

---

## 💬 Configuration WhatsApp Business

### Option 1 : WhatsApp Business Simple (Gratuit - Recommandé)

C'est la méthode actuellement configurée. Elle utilise le lien `wa.me` pour rediriger vers WhatsApp.

#### Configuration :

1. Téléchargez **WhatsApp Business** sur votre téléphone
2. Créez un compte avec votre numéro professionnel
3. Dans l'admin Django (`/admin/`), allez dans **Site Settings** ou mettez à jour le fichier `.env` :

```
WHATSAPP_NUMBER=50937773508
```

**Format du numéro** : Code pays + numéro sans espaces ni caractères spéciaux
- Haiti : `509` + numéro → `50937773508`
- France : `33` + numéro (sans le 0) → `33612345678`
- Canada : `1` + numéro → `15141234567`

### Option 2 : WhatsApp Business API (Payant)

Pour une intégration plus avancée avec automatisation :

1. Allez sur : https://business.facebook.com/
2. Créez un compte Meta Business
3. Configurez l'API WhatsApp Business
4. Obtenez votre token d'accès

*Cette option nécessite des modifications de code supplémentaires.*

---

## 🔐 Variables d'environnement PythonAnywhere

### Méthode 1 : Fichier .env (Recommandé)

Créez un fichier `/home/smile/.env` :

```bash
# ===========================================
# CONFIGURATION SMILE E-COMMERCE
# ===========================================

# Clé secrète Django (OBLIGATOIRE - Changez cette valeur!)
DJANGO_SECRET_KEY=votre-cle-secrete-tres-longue-et-complexe-ici-12345

# Configuration Email Gmail
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-application-16-caracteres

# WhatsApp Business
WHATSAPP_NUMBER=50937773508

# Mode Debug (False en production!)
DEBUG=False
```

### Méthode 2 : Configuration WSGI

Éditez `/var/www/smile_pythonanywhere_com_wsgi.py` :

```python
import os
import sys

# Configuration des variables d'environnement
os.environ['DJANGO_SECRET_KEY'] = 'votre-cle-secrete-ici'
os.environ['EMAIL_HOST_USER'] = 'votre-email@gmail.com'
os.environ['EMAIL_HOST_PASSWORD'] = 'votre-mot-de-passe-app'
os.environ['WHATSAPP_NUMBER'] = '50937773508'

# Chemin du projet
path = '/home/smile/smile'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'smile.settings_pythonanywhere'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Générer une SECRET_KEY sécurisée

Exécutez cette commande dans la console Python de PythonAnywhere :

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

---

## 🌐 Déploiement sur PythonAnywhere

### Étape 1 : Mettre à jour le code

```bash
cd ~/smile
git pull origin main
```

### Étape 2 : Installer les dépendances (si nécessaire)

```bash
workon smileenv
pip install -r requirements.txt
```

### Étape 3 : Appliquer les migrations

```bash
cd smile
python manage.py migrate --settings=smile.settings_pythonanywhere
```

### Étape 4 : Collecter les fichiers statiques

```bash
python manage.py collectstatic --noinput --settings=smile.settings_pythonanywhere
```

### Étape 5 : Recharger le site

1. Allez dans **Web** sur PythonAnywhere
2. Cliquez sur le bouton vert **"Reload"**

---

## ✅ Vérification de la configuration

### Tester l'envoi d'email

Dans la console Python de PythonAnywhere :

```python
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smile.settings_pythonanywhere')

import django
django.setup()

from django.core.mail import send_mail

send_mail(
    subject='Test Smile E-commerce',
    message='Si vous recevez cet email, la configuration fonctionne!',
    from_email='votre-email@gmail.com',
    recipient_list=['votre-email@gmail.com'],
    fail_silently=False,
)
print("Email envoyé avec succès!")
```

### Tester les templates d'email

```python
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smile.settings_pythonanywhere')

import django
django.setup()

from core.email_service import send_welcome_email

# Remplacez par un vrai email pour tester
send_welcome_email(
    user_email='votre-email@gmail.com',
    user_name='Test User'
)
print("Email de bienvenue envoyé!")
```

### Vérifier WhatsApp

1. Ouvrez votre site : https://smile.pythonanywhere.com
2. Vérifiez que le bouton WhatsApp flottant apparaît en bas à droite
3. Cliquez dessus - il devrait ouvrir WhatsApp avec un message pré-rempli
4. Sur une page produit, vérifiez le bouton "Commander via WhatsApp"

---

## 📨 Utilisation des emails dans le code

### Emails disponibles

Le service d'email (`core/email_service.py`) fournit les fonctions suivantes :

```python
from core.email_service import (
    send_order_confirmation,    # Confirmation de commande
    send_order_shipped,         # Notification d'expédition
    send_order_cancelled,       # Annulation de commande
    send_order_delivered,       # Confirmation de livraison
    send_payment_confirmed,     # Confirmation de paiement
    send_payment_failed,        # Échec de paiement
    send_refund_processed,      # Remboursement traité
    send_contact_notification,  # Notification de contact
    send_welcome_email,         # Email de bienvenue
    send_password_reset,        # Réinitialisation mot de passe
    send_back_in_stock,         # Retour en stock
    send_cart_abandoned,        # Panier abandonné
    send_invoice,               # Facture
    send_newsletter,            # Newsletter
)
```

### Exemples d'utilisation

#### Confirmation de commande

```python
from core.email_service import send_order_confirmation

send_order_confirmation(
    order=order_object,  # Instance de Order
    user_email='client@email.com',
    user_name='Jean Dupont'
)
```

#### Email de bienvenue après inscription

```python
# Dans votre vue d'inscription
from core.email_service import send_welcome_email

def register_view(request):
    # ... logique d'inscription ...
    
    send_welcome_email(
        user_email=user.email,
        user_name=user.get_full_name() or user.username
    )
```

#### Notification d'expédition

```python
from core.email_service import send_order_shipped

send_order_shipped(
    order=order,
    user_email=order.user.email,
    user_name=order.user.get_full_name(),
    tracking_number='TRK123456789',
    carrier='DHL'
)
```

#### Panier abandonné

```python
from core.email_service import send_cart_abandoned

send_cart_abandoned(
    user_email='client@email.com',
    user_name='Jean',
    cart_items=[
        {'name': 'Robe d\'été', 'price': '49.99', 'image_url': 'http://...'},
        {'name': 'Sac à main', 'price': '89.99', 'image_url': 'http://...'},
    ],
    cart_total='139.98',
    cart_url='https://smile.pythonanywhere.com/panier/'
)
```

---

## 🔧 Dépannage

### Problème : Email non envoyé

**Vérifications :**

1. **Validation en deux étapes activée ?**
   - Allez sur https://myaccount.google.com/security

2. **Mot de passe d'application correct ?**
   - Le mot de passe doit être de 16 caractères SANS espaces
   - Régénérez un nouveau si nécessaire

3. **Variables d'environnement configurées ?**
   ```bash
   # Dans la console PythonAnywhere
   echo $EMAIL_HOST_USER
   echo $EMAIL_HOST_PASSWORD
   ```

4. **"Accès aux applications moins sécurisées" ?**
   - Cette option n'existe plus, utilisez les mots de passe d'application

### Problème : SMTPAuthenticationError

```
SMTPAuthenticationError: (535, '5.7.8 Username and Password not accepted')
```

**Solution :**
- Vérifiez que vous utilisez un **mot de passe d'application** et non votre mot de passe Gmail normal
- Régénérez un nouveau mot de passe d'application

### Problème : WhatsApp ne s'ouvre pas

**Vérifications :**

1. Format du numéro correct (code pays sans +)
2. WhatsApp installé sur l'appareil de test
3. Vérifiez la console du navigateur (F12) pour les erreurs JavaScript

### Problème : Erreur 500 après déploiement

1. Vérifiez les logs d'erreur :
   ```bash
   # Dans la console PythonAnywhere
   tail -100 /var/log/smile.pythonanywhere.com.error.log
   ```

2. Vérifiez que toutes les variables d'environnement sont configurées

3. Relancez les migrations :
   ```bash
   python manage.py migrate --settings=smile.settings_pythonanywhere
   ```

---

## 📱 Fonctionnalités WhatsApp

### Bouton flottant
- Apparaît sur toutes les pages en bas à droite
- Message pré-rempli : "Bonjour! Je visite votre boutique Smile et j'ai une question."

### Bouton produit
- Apparaît sur chaque page produit
- Message pré-rempli avec le nom du produit et le prix

### Personnaliser les messages

Éditez les templates dans :
- `templates/base.html` - Bouton flottant
- `templates/shop/product_detail.html` - Bouton produit

---

## 📊 Récapitulatif des URLs importantes

| Description | URL |
|-------------|-----|
| Site | https://smile.pythonanywhere.com |
| Admin Django | https://smile.pythonanywhere.com/admin/ |
| Sécurité Google | https://myaccount.google.com/security |
| Mots de passe app | https://myaccount.google.com/apppasswords |
| PythonAnywhere | https://www.pythonanywhere.com |

---

## 🎉 Checklist finale

- [ ] Validation en deux étapes Gmail activée
- [ ] Mot de passe d'application Gmail créé
- [ ] Variables d'environnement configurées sur PythonAnywhere
- [ ] Code à jour (`git pull`)
- [ ] Migrations appliquées
- [ ] Fichiers statiques collectés
- [ ] Site rechargé
- [ ] Test d'envoi d'email réussi
- [ ] Bouton WhatsApp fonctionnel
- [ ] Bouton WhatsApp produit fonctionnel

---

## 📞 Support

Pour toute question, contactez le développeur ou consultez la documentation Django :
- https://docs.djangoproject.com/
- https://help.pythonanywhere.com/

**Bonne vente avec Smile! 😊🛍️**
