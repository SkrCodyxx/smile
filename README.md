# 😊 Smile Shop - Application E-commerce

Application e-commerce complète avec gestion de stock et facturation, développée avec Django.

![Django](https://img.shields.io/badge/Django-4.2-green?logo=django)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)
![Deploy](https://img.shields.io/badge/Deploy-PythonAnywhere-1D9FD7)

## 🌐 Site en ligne

**https://smile.pythonanywhere.com**

## 📱 Fonctionnalités

- 🎨 **Design moderne** - Thème sombre élégant avec animations
- 🌍 **Multi-langues** - Français, English, Kreyòl Ayisyen
- 💱 **Multi-devises** - EUR, USD, CAD, HTG
- 🛒 **Panier coulissant** - Interface intuitive
- 📦 **Gestion des produits** - Catégories, variantes, stock
- 🧾 **Facturation** - Génération PDF automatique
- 📊 **Dashboard Admin** - Statistiques et analyses

## 🏗️ Architecture

```
smile/
├── docker-compose.yml      # Docker (développement local)
├── nginx/nginx.conf        # Configuration Nginx
└── smile/                  # Application Django
    ├── core/               # Configuration du site
    ├── shop/               # Boutique (produits, panier)
    ├── invoicing/          # Facturation
    ├── templates/          # Templates HTML
    ├── static/             # CSS, JS, images
    ├── locale/             # Traductions (fr, en, ht)
    └── media/              # Fichiers uploadés
```

## 🚀 Développement local (Docker)

```bash
# Démarrer
docker-compose up -d

# Migrations
docker-compose exec web python manage.py migrate

# Créer admin
docker-compose exec web python manage.py createsuperuser

# Accéder
open http://localhost
```

## 🌐 Déploiement PythonAnywhere

Voir le guide complet : [DEPLOIEMENT_PYTHONANYWHERE.md](DEPLOIEMENT_PYTHONANYWHERE.md)

## 📝 Variables d'environnement

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Clé secrète Django |
| `DEBUG` | Mode debug (False en prod) |
| `DATABASE_URL` | URL de la base de données |
| `DB_PASSWORD` | Mot de passe MySQL |

## 📄 License

MIT License

---

Développé avec ❤️
