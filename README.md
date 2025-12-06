# 😊 Smile Shop - Application E-commerce

Application e-commerce complète avec gestion de stock et facturation, développée avec Django.

![Django](https://img.shields.io/badge/Django-4.2-green?logo=django)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)
![Deploy](https://img.shields.io/badge/Deploy-Render.com-46E3B7?logo=render)

## 🌐 Déploiement sur Render.com

### Méthode Blueprint (Recommandé)

1. **Push** ce repo sur GitHub
2. Connectez-vous à [Render.com](https://render.com)
3. Cliquez sur **New** → **Blueprint**
4. Sélectionnez votre repo
5. Render créera automatiquement:
   - 🖥️ Web Service (Django + Gunicorn)
   - 🗄️ PostgreSQL Database

### Variables d'environnement (configurées automatiquement)
- `DATABASE_URL` - URL PostgreSQL
- `SECRET_KEY` - Générée automatiquement
- `DEBUG=False`
- `ALLOWED_HOSTS=.onrender.com`

## 🏗️ Architecture

```
app1/
├── docker-compose.yml      # Configuration Docker
├── nginx/
│   └── nginx.conf          # Configuration Nginx
└── smile/                  # Application Django
    ├── manage.py
    ├── smile/              # Configuration Django
    ├── core/               # Configuration du site (NOUVEAU)
    ├── shop/               # App boutique (produits, panier)
    ├── invoicing/          # App facturation (commandes, factures)
    ├── templates/          # Templates HTML
    ├── static/             # Fichiers statiques
    ├── locale/             # Traductions (fr, en, ht)
    └── media/              # Fichiers uploadés
```

## 🚀 Démarrage rapide

### 1. Lancer avec Docker (Production)

```bash
# Démarrer tous les services
docker-compose up -d

# Appliquer les migrations
docker-compose exec web python manage.py migrate

# Charger les paramètres initiaux
docker-compose exec web python manage.py loaddata initial_settings

# Créer un superutilisateur
docker-compose exec web python manage.py createsuperuser
```

L'application sera accessible sur :
- **Boutique** : http://localhost
- **Administration** : http://localhost/admin
- **Dashboard Analytics** : http://localhost/admin/dashboard/

### 2. Développement local

```bash
cd smile

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
export DEBUG=True
export DB_HOST=localhost
# ... (voir .env.example)

# Appliquer les migrations
python manage.py migrate

# Créer un admin
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

## 📱 Fonctionnalités

### Partie Publique (Boutique)
- 🏠 Page d'accueil avec produits en vedette et bannières
- 🔍 Recherche simple et avancée avec filtres
- 📂 Navigation par catégories
- 🛒 Panier d'achat
- ⭐ Avis et notes produits
- ❤️ Liste de souhaits (wishlist)
- 🎨 Variantes produits (taille, couleur)
- 💳 Processus de commande
- 👤 Compte client (commandes, factures, favoris)
- 🌍 Multi-langues (Français, English, Kreyòl)

### Partie Admin (Django Admin)

#### ⚙️ Configuration du site (core)
- 🏪 **Paramètres généraux** : Nom, logo, slogan, devise, TVA
- 📞 **Contacts illimités** : Emails, téléphones, WhatsApp
- 📍 **Adresses illimitées** : Avec coordonnées GPS
- 📧 **Configuration email** : SMTP Gmail avec test intégré
- 💳 **Paiements** : PayPal, Stripe, Virement, À la livraison
- 🚚 **Livraison** : Méthodes multiples avec tarifs
- 📝 **Champs personnalisés** : Ajoutez n'importe quelle info
- 🎨 **Bannières** : Hero, promos, annonces programmables
- 📄 **Pages légales** : CGV, mentions légales dynamiques
- 🔢 **Numérotation** : Commandes, factures, SKU automatiques

#### 🛍️ Boutique
- 📦 **Gestion des produits** avec images, prix, stock
- ⭐ **Avis clients** avec modération
- ❤️ **Wishlists** des utilisateurs
- 🎨 **Variantes** : Taille, couleur, etc.
- 📊 **Stock** : Alertes, mouvements, seuils

#### 🧾 Facturation
- 📋 **Commandes** : Suivi complet des statuts
- 💰 **Factures** : Génération automatique, PDF
- 👥 **Clients** : Profils, historique

#### 📊 Dashboard Analytics
- 💰 CA jour/semaine/mois
- 📦 Commandes et paniers moyens
- 🔴 Alertes stock et commandes
- 📈 Graphiques d'évolution
- 🏆 Top produits vendus

## 🔒 Sécurité

- ✅ Tous les services internes (DB, Redis, Backend) sont isolés dans un réseau Docker privé
- ✅ Seul Nginx (port 80) est exposé
- ✅ Protection CSRF activée
- ✅ Rate limiting sur l'API
- ✅ Headers de sécurité (Helmet)

## 🛠️ Technologies

- **Backend** : Django 4.2, Python 3.11
- **Base de données** : PostgreSQL 15
- **Cache** : Redis 7
- **Serveur web** : Nginx + Gunicorn
- **Frontend** : Bootstrap 5, HTML/CSS/JS
- **Containerisation** : Docker & Docker Compose

## 📝 Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `DEBUG` | Mode debug | `False` |
| `SECRET_KEY` | Clé secrète Django | (requis) |
| `DATABASE_URL` | URL de connexion PostgreSQL | - |
| `REDIS_URL` | URL de connexion Redis | - |
| `ALLOWED_HOSTS` | Hosts autorisés | `localhost` |

## 👤 Accès Admin par défaut

Après le premier lancement, créez un superutilisateur :

```bash
docker-compose exec web python manage.py createsuperuser
```

## 📄 License

MIT License - Libre d'utilisation pour tout projet.

---

Développé avec ❤️ pour Smile Shop
