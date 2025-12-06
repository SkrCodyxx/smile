# 🚀 Guide de Déploiement - PythonAnywhere + Supabase

## 📋 Informations du projet

- **Username PythonAnywhere** : `smile`
- **Base de données** : Supabase PostgreSQL (gratuit)
- **URL Supabase** : `db.crieerueopsntuhraatj.supabase.co`
- **Repo GitHub** : `https://github.com/SkrCodyxx/smile.git`

---

## Étape 1: Cloner le projet

Dans la console Bash PythonAnywhere :

```bash
cd ~
git clone https://github.com/SkrCodyxx/smile.git
cd smile/smile
```

---

## Étape 2: Créer l'environnement virtuel

```bash
mkvirtualenv --python=/usr/bin/python3.10 smileenv
workon smileenv
pip install -r requirements.txt
```

---

## Étape 3: Appliquer les migrations (vers Supabase)

```bash
python manage.py migrate --settings=smile.settings_pythonanywhere
```

---

## Étape 4: Collecter les fichiers statiques

```bash
python manage.py collectstatic --noinput --settings=smile.settings_pythonanywhere
```

---

## Étape 5: Créer un superuser

```bash
python manage.py createsuperuser --settings=smile.settings_pythonanywhere
```

---

## Étape 6: Créer les données initiales

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

## Étape 7: Configurer l'application Web

### 7.1 Créer l'app web
1. Va dans l'onglet **"Web"**
2. Clique **"Add a new web app"**
3. Clique **"Next"** (accepte le domaine `smile.pythonanywhere.com`)
4. Choisis **"Manual configuration"**
5. Sélectionne **Python 3.10**

### 7.2 Configurer les chemins

Dans la section **"Code"** :
- **Source code** : `/home/smile/smile/smile`
- **Working directory** : `/home/smile/smile/smile`

### 7.3 Configurer le virtualenv

Dans la section **"Virtualenv"** :
- Chemin : `/home/smile/.virtualenvs/smileenv`

### 7.4 Éditer le fichier WSGI

Clique sur le lien du fichier WSGI (`/var/www/smile_pythonanywhere_com_wsgi.py`)

**Supprime TOUT le contenu** et remplace par :

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
os.environ['DATABASE_URL'] = 'postgresql://postgres:Sm%21le2000Sm%21@db.crieerueopsntuhraatj.supabase.co:5432/postgres'

# Application WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Sauvegarde le fichier !**

---

## Étape 8: Configurer les fichiers statiques

Dans l'onglet **"Web"**, section **"Static files"**, clique "Add" :

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/smile/smile/smile/staticfiles` |
| `/media/` | `/home/smile/smile/smile/media` |

---

## Étape 9: Lancer le site ! 🎉

1. Clique le gros bouton vert **"Reload"** en haut de la page
2. Visite ton site : **https://smile.pythonanywhere.com**
3. Admin : **https://smile.pythonanywhere.com/admin**

---

## 🔄 Mettre à jour le site

Quand tu fais des changements sur GitHub :

```bash
cd ~/smile
git pull
workon smileenv
cd smile
python manage.py migrate --settings=smile.settings_pythonanywhere
python manage.py collectstatic --noinput --settings=smile.settings_pythonanywhere
```

Puis clique **"Reload"** dans l'onglet Web.

---

## ❓ Dépannage

### Erreur 500 ?
Regarde les logs :
- Dans l'onglet **Web** → **Error log**
- Ou : `cat /var/log/smile.pythonanywhere.com.error.log`

### "DisallowedHost" ?
Vérifie que `ALLOWED_HOSTS` contient `.pythonanywhere.com`

### Base de données ne se connecte pas ?
Vérifie l'URL Supabase dans le fichier WSGI

### Fichiers statiques cassés ?
```bash
workon smileenv
cd ~/smile/smile
python manage.py collectstatic --noinput --settings=smile.settings_pythonanywhere
```
Puis **Reload**.

---

## ✅ Checklist finale

- [ ] Code cloné dans `/home/smile/smile`
- [ ] Virtualenv `smileenv` créé
- [ ] Dépendances installées
- [ ] Migrations appliquées (Supabase)
- [ ] Fichiers statiques collectés
- [ ] Superuser créé
- [ ] App web configurée
- [ ] WSGI configuré
- [ ] Static files configurés
- [ ] Site rechargé et fonctionnel ! 🎉

---

**Ton site** : https://smile.pythonanywhere.com
**Admin** : https://smile.pythonanywhere.com/admin
