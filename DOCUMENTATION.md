# 📚 Documentation Fonctionnelle - Smile Shop

## Vue d'ensemble

Smile Shop est une application e-commerce complète développée avec Django. Elle comprend une **partie publique** (boutique en ligne) et une **partie administration** (gestion du stock et facturation).

---

## 🛒 PARTIE PUBLIQUE (Boutique)

### Pages disponibles

| Page | URL | Description |
|------|-----|-------------|
| Accueil | `/` | Page d'accueil avec produits vedettes et catégories |
| Produits | `/products/` | Liste de tous les produits avec recherche et tri |
| Catégorie | `/category/<slug>/` | Produits d'une catégorie |
| Détail produit | `/product/<slug>/` | Fiche détaillée d'un produit |
| Panier | `/cart/` | Panier d'achat |
| Commande | `/checkout/` | Finalisation de commande (connexion requise) |
| Inscription | `/register/` | Créer un compte |
| Connexion | `/accounts/login/` | Se connecter |
| Profil | `/profile/` | Modifier ses informations |
| Commandes | `/invoices/orders/` | Historique des commandes |
| Factures | `/invoices/` | Mes factures |
| Contact | `/contact/` | Formulaire de contact |
| À propos | `/about/` | Page à propos |
| CGV | `/cgv/` | Conditions générales de vente |
| Mentions légales | `/legal/` | Mentions légales et RGPD |

---

## 🔄 Parcours client

### 1. Navigation et découverte
```
Accueil → Catégories / Recherche → Liste produits → Détail produit
```

### 2. Achat
```
Détail produit → Ajouter au panier → Panier → Commande → Confirmation
```

### 3. Suivi
```
Connexion → Mes commandes → Détail commande → Facture (PDF)
```

---

## 📦 Fonctionnalités détaillées

### 🏠 Page d'accueil
- Produits **mis en avant** (is_featured = true)
- **Nouveautés** (derniers produits ajoutés)
- Navigation par **catégories**
- Barre de **recherche** globale

### 📋 Liste des produits
- **Pagination** (12 produits par page)
- **Recherche** par nom, description, SKU
- **Tri** par :
  - Plus récents (défaut)
  - Prix croissant
  - Prix décroissant
  - Nom A-Z
- **Filtrage** par catégorie

### 🔍 Détail produit
- Image principale + galerie
- Prix (avec prix barré si promo)
- Badge de réduction (%)
- Indicateur de **stock** :
  - 🟢 En stock
  - 🟡 Stock bas (< seuil)
  - 🔴 Rupture
- Produits **similaires**
- Bouton **Ajouter au panier**
- Bouton **Wishlist** ❤️
- **Avis clients** avec notes ⭐
- **Variantes** (taille, couleur) si disponibles

### ⭐ Avis Produits (NOUVEAU)
- Note de 1 à 5 étoiles
- Titre et commentaire
- Badge "Achat vérifié" si le client a acheté
- Vote "Utile" sur les avis
- Distribution des notes (graphique)
- Note moyenne affichée
- **Modération** : les avis doivent être approuvés

### ❤️ Wishlist / Favoris (NOUVEAU)
- Ajouter/retirer des favoris depuis la liste ou le détail produit
- Page "Ma liste de souhaits"
- Déplacer vers le panier en un clic
- Compteur dans la navbar

### 🔎 Recherche Avancée (NOUVEAU)
- Recherche par **mots-clés**
- Filtre par **catégorie**
- Filtre par **prix** (min/max)
- Filtre par **note minimum**
- Option **En stock uniquement**
- Option **En promotion**

### 🎨 Variantes Produits (NOUVEAU)
- Attributs configurables (Taille, Couleur, etc.)
- Chaque variante peut avoir :
  - Son propre SKU
  - Un ajustement de prix (+/-)
  - Son propre stock
  - Sa propre image
- Sélection visuelle sur la fiche produit

### 🛒 Panier
- Liste des articles
- Modification des **quantités**
- Suppression d'articles
- Calcul automatique :
  - Sous-total
  - TVA (20%)
  - Frais de port (gratuit dès 50€)
  - **Total**
- Indicateur livraison gratuite

### ✅ Commande (Checkout)
- **Connexion requise**
- Formulaire d'adresse :
  - Livraison
  - Facturation (identique ou différente)
- Récapitulatif de commande
- Notes de commande
- **Décrément automatique du stock**
- Génération du numéro de commande

### 👤 Compte utilisateur
- **Inscription** :
  - Prénom, Nom, Email
  - Mot de passe (min. 8 caractères)
  - Acceptation CGV
  - Connexion automatique après inscription
- **Profil** :
  - Modification des infos personnelles
  - Adresse de livraison par défaut
  - Infos entreprise (optionnel)
- **Historique** :
  - Liste des commandes avec statuts
  - Détail de chaque commande
  - Liste des factures
  - Téléchargement PDF

---

## 🔐 PARTIE ADMIN (Django Admin)

### Accès
- **URL** : `/admin/`
- **Identifiants** : Créer avec `python manage.py createsuperuser`

### 📊 Tableau de bord

L'admin Django permet de gérer :

#### 🛍️ Boutique (shop)
| Section | Fonctionnalités |
|---------|-----------------|
| **Catégories** | CRUD, image, parent, slug auto |
| **Produits** | CRUD, prix, stock, images, SEO |
| **Mouvements de stock** | Entrées, sorties, ajustements |
| **Coupons** | Codes promo, % ou fixe, dates |
| **Paniers** | Visualisation des paniers en cours |

#### 📄 Facturation (invoicing)
| Section | Fonctionnalités |
|---------|-----------------|
| **Commandes** | Statuts, paiement, expédition |
| **Factures** | Génération, statuts, PDF |
| **Clients** | Profils, infos entreprise |

#### ⚙️ Configuration du site (core) - NOUVEAU
| Section | Fonctionnalités |
|---------|-----------------|
| **Configuration du site** | Nom, logo, slogan, devise, TVA, numérotation |
| **Contacts** | Emails, téléphones, WhatsApp (illimités) |
| **Adresses** | Adresses multiples avec GPS |
| **Configuration Email** | SMTP Gmail avec test intégré |
| **Configuration Paiement** | PayPal, Stripe, Virement, À la livraison |
| **Méthodes de livraison** | Tarifs, délais, livraison gratuite |
| **Champs personnalisés** | Ajouter n'importe quelle info |
| **Bannières** | Hero, promos, annonces programmables |
| **Pages légales** | CGV, Mentions légales, Confidentialité |

### ⚙️ Actions rapides

**Sur les commandes :**
- ✅ Marquer comme confirmée
- 🚚 Marquer comme expédiée
- ✔️ Marquer comme livrée
- 📄 Générer une facture

**Sur les factures :**
- 📧 Marquer comme envoyée
- ✅ Marquer comme payée

**Sur les avis :**
- ✅ Approuver les avis
- ❌ Rejeter les avis

### 📊 Dashboard Analytics (NOUVEAU)

Accès : `/admin/dashboard/`

**Métriques principales :**
- 💰 CA du jour / du mois / 30 derniers jours
- 📦 Nombre de commandes
- 🛒 Panier moyen
- 👥 Nouveaux clients

**Alertes :**
- 🔴 Produits en rupture de stock
- 🟡 Produits en stock bas
- ⏳ Commandes en attente
- 📝 Avis à modérer
- 💳 Factures impayées
- 🛒 Paniers abandonnés

**Graphique :**
- Évolution CA et commandes sur 30 jours

**Classements :**
- Top 5 produits les plus vendus
- Dernières commandes

### 📈 Indicateurs visuels

- **Stock** : Couleurs (🟢🟡🔴) + quantité
- **Prix** : Prix barré si promo + prix actuel
- **Marges** : Calcul automatique si coût renseigné
- **Statuts** : Badges colorés

---

## 📊 Modèles de données

### Produit (Product)
```
- name, slug, description
- price, compare_at_price, cost_price
- sku, barcode
- category (FK)
- stock_quantity, low_stock_threshold
- is_active, is_featured
- images (relation)
```

### Commande (Order)
```
- order_number (auto: CMD-000001)
- user (FK)
- status: pending → confirmed → processing → shipped → delivered
- payment_status: pending → paid
- subtotal, tax, shipping, discount, total
- shipping_address, billing_address
- tracking_number
```

### Facture (Invoice)
```
- invoice_number (auto: FAC-2024-00001)
- order (OneToOne)
- status: draft → sent → paid
- issue_date, due_date
- subtotal, tax_rate, tax_amount, total
```

### Avis (ProductReview) - NOUVEAU
```
- product (FK)
- user (FK)
- rating (1-5)
- title, comment
- is_approved, is_verified_purchase
- helpful_votes
```

### Wishlist - NOUVEAU
```
- user (OneToOne)
- products (ManyToMany)
```

### Variante Produit (ProductVariant) - NOUVEAU
```
- product (FK)
- sku, name
- attributes (ManyToMany → VariantAttributeValue)
- price_adjustment
- stock_quantity
- image
```

---

## 🌍 Multi-langues (NOUVEAU)

### Langues supportées
| Code | Langue | Drapeau |
|------|--------|---------|
| `fr` | Français | 🇫🇷 |
| `en` | English | 🇬🇧 |
| `ht` | Kreyòl Ayisyen | 🇭🇹 |

### Comment changer de langue
- Cliquer sur l'icône 🌐 dans la navbar
- Choisir la langue souhaitée
- La préférence est sauvegardée dans un cookie

### Fichiers de traduction
```
smile/locale/
├── fr/LC_MESSAGES/django.po   # Français
├── en/LC_MESSAGES/django.po   # Anglais
└── ht/LC_MESSAGES/django.po   # Créole haïtien
```

### Ajouter une traduction
1. Modifier le fichier `.po` correspondant
2. Compiler avec `python manage.py compilemessages`

---

## 🔒 Sécurité

- **Authentification** : Django auth standard
- **Permissions** : Login requis pour commander
- **CSRF** : Protection sur tous les formulaires
- **Stock** : Vérification avant ajout au panier
- **Admin** : Réservé aux staff/superusers

---

## 🎨 Design

- **Framework CSS** : Bootstrap 5.3
- **Icônes** : Bootstrap Icons
- **Couleurs** :
  - Primary: #6366f1 (violet)
  - Secondary: #8b5cf6
  - Success: #10b981
  - Danger: #ef4444
- **Responsive** : Mobile-first

---

## ⚡ Configuration

### Variables importantes (`settings.py`)
```python
TAX_RATE = 20              # TVA en %
FREE_SHIPPING_THRESHOLD = 50   # Livraison gratuite dès X€
SHIPPING_COST = 5.99       # Frais de port
CURRENCY = 'EUR'
CURRENCY_SYMBOL = '€'
```

---

## 🚀 Démarrage

```bash
# Docker (production)
docker-compose up -d
docker-compose exec web python manage.py createsuperuser

# Local (développement)
cd smile
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## ✅ Checklist des fonctionnalités

### Boutique publique
- [x] Page d'accueil
- [x] Liste des produits
- [x] Navigation par catégories
- [x] Recherche de produits
- [x] **Recherche avancée** (filtres prix, stock, promo, note)
- [x] Tri des produits
- [x] Détail produit
- [x] **Prix barré avec remise bien visible**
- [x] Panier d'achat
- [x] Processus de commande
- [x] Inscription / Connexion
- [x] Profil utilisateur
- [x] Historique commandes
- [x] Factures client
- [x] **Avis et notes produits** ⭐
- [x] **Wishlist / Favoris** ❤️
- [x] Page contact
- [x] Page à propos
- [x] CGV
- [x] Mentions légales
- [x] **Multi-langues** 🌍 (FR/EN/Créole Haïtien)

### Administration
- [x] Gestion des produits
- [x] Gestion des catégories
- [x] Gestion du stock
- [x] Mouvements de stock
- [x] Commandes
- [x] Factures
- [x] Coupons de réduction
- [x] Clients
- [x] **Modération des avis**
- [x] **Variantes produits** (taille, couleur)
- [x] **Dashboard Analytics** 📊

### À ajouter (optionnel)
- [ ] Paiement en ligne (Stripe)
- [ ] Emails transactionnels
- [ ] Newsletter
- [ ] Programme fidélité
