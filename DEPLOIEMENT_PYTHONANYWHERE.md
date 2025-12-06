# 🚀 Guide de Déploiement - PythonAnywhere

## 📋 Informations

- **Site** : https://smile.pythonanywhere.com
- **Username** : `smile`
- **Base de données** : MySQL PythonAnywhere (gratuit)

---

## 1️⃣ Créer la base de données MySQL

1. Va dans l'onglet **"Databases"** sur PythonAnywhere
2. Crée un mot de passe MySQL : `Sm!le2000Sm!`
3. Clique **"Initialize MySQL"**
4. Crée une nouvelle base : `smile_db`
   - Nom complet : `smile$smile_db`

---

## 2️⃣ Cloner le projet

```bash
cd ~
git clone https://github.com/SkrCodyxx/smile.git
cd smile/smile
```

---

## 3️⃣ Créer l'environnement virtuel

```bash
mkvirtualenv --python=/usr/bin/python3.10 smileenv
workon smileenv
pip install -r requirements.txt
```

---

## 4️⃣ Appliquer les migrations

```bash
python manage.py migrate --settings=smile.settings_pythonanywhere
```

---

## 5️⃣ Collecter les fichiers statiques

```bash
python manage.py collectstatic --noinput --settings=smile.settings_pythonanywhere
```

---

## 6️⃣ Créer un superuser

```bash
python manage.py createsuperuser --settings=smile.settings_pythonanywhere
```

---

## 7️⃣ Créer les données initiales

```bash
python manage.py shell --settings=smile.settings_pythonanywhere << 'EOF'
from core.models import Language, Currency

# Langues
for code, name, default in [('fr', 'Français', True), ('en', 'English', False), ('ht', 'Kreyòl Ayisyen', False)]:
    Language.objects.get_or_create(code=code, defaults={'name': name, 'is_active': True, 'is_default': default})
    print(f"✅ Langue: {name}")

# Devises  
for code, name, symbol, rate, default in [('EUR', 'Euro', '€', 1.0, True), ('USD', 'Dollar US', '$', 1.09, False), ('CAD', 'Dollar Canadien', 'CA$', 1.49, False), ('HTG', 'Gourde Haïtienne', 'G', 143.50, False)]:
    Currency.objects.get_or_create(code=code, defaults={'name': name, 'symbol': symbol, 'rate': rate, 'is_active': True, 'is_default': default})
    print(f"✅ Devise: {name}")

print("🎉 Données créées!")
EOF
```

---

## 8️⃣ Configurer l'application Web

### 8.1 Créer l'app web
1. Onglet **"Web"** → **"Add a new web app"**
2. **"Next"** (accepte `smile.pythonanywhere.com`)
3. **"Manual configuration"** → **Python 3.10**

### 8.2 Configurer les chemins

| Paramètre | Valeur |
|-----------|--------|
| **Source code** | `/home/smile/smile/smile` |
| **Working directory** | `/home/smile/smile/smile` |
| **Virtualenv** | `/home/smile/.virtualenvs/smileenv` |

### 8.3 Éditer le fichier WSGI

Clique sur le lien WSGI et remplace TOUT par :

```python
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
```

### 8.4 Configurer les fichiers statiques

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/smile/smile/smile/staticfiles` |
| `/media/` | `/home/smile/smile/smile/media` |

---

## 9️⃣ Lancer le site ! 🎉

1. Clique **"Reload"** (bouton vert)
2. Visite : **https://smile.pythonanywhere.com**
3. Admin : **https://smile.pythonanywhere.com/admin**

---

## 🔄 Mettre à jour le site

```bash
cd ~/smile
git pull
cd smile
workon smileenv
python manage.py migrate --settings=smile.settings_pythonanywhere
python manage.py collectstatic --noinput --settings=smile.settings_pythonanywhere
```

Puis clique **"Reload"** dans l'onglet Web.

---

## ❓ Dépannage

### Erreur 500 ?
- Onglet **Web** → **Error log**

### Base de données ?
- Vérifie que `smile$smile_db` existe dans l'onglet Databases
- Vérifie le mot de passe MySQL

### Fichiers statiques cassés ?
```bash
workon smileenv
cd ~/smile/smile
python manage.py collectstatic --noinput --settings=smile.settings_pythonanywhere
```
