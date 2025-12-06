# 🚀 Guide de Déploiement - PythonAnywhere

## Étape 1: Créer un compte

1. Va sur **https://www.pythonanywhere.com**
2. Clique sur **"Start running Python online"**
3. Choisis **"Create a Beginner account"** (gratuit)
4. Note ton **username** (tu en auras besoin)

---

## Étape 2: Uploader ton code

### Option A: Depuis GitHub (Recommandé)

1. Push ton code sur GitHub d'abord
2. Sur PythonAnywhere, va dans **"Consoles"** → **"Bash"**
3. Clone ton repo:
```bash
git clone https://github.com/TONUSERNAME/smile-shop.git smile
cd smile
```

### Option B: Upload manuel

1. Va dans **"Files"**
2. Crée un dossier `smile`
3. Upload tous les fichiers du dossier `smile/` de ton projet

---

## Étape 3: Créer l'environnement virtuel

Dans la console Bash:

```bash
cd ~
mkvirtualenv --python=/usr/bin/python3.11 smile-env
workon smile-env
cd smile
pip install -r requirements.txt
pip install mysqlclient
```

---

## Étape 4: Créer la base de données

1. Va dans l'onglet **"Databases"**
2. Définis un **mot de passe MySQL** et clique "Initialize"
3. Crée une nouvelle base: `smile_db`
   - Le nom complet sera: `TONUSERNAME$smile_db`

---

## Étape 5: Configurer les settings

1. Va dans **"Files"** → `smile/smile/settings_pythonanywhere.py`
2. Remplace `TONUSERNAME` par ton vrai username (3 endroits)
3. Ajoute ton mot de passe MySQL

---

## Étape 6: Créer l'application web

1. Va dans l'onglet **"Web"**
2. Clique **"Add a new web app"**
3. Choisis **"Manual configuration"**
4. Sélectionne **Python 3.11**

### Configurer le virtualenv:
- Dans "Virtualenv", entre: `/home/TONUSERNAME/.virtualenvs/smile-env`

### Configurer le WSGI:
1. Clique sur le lien du fichier WSGI
2. **Supprime tout le contenu**
3. Copie-colle le contenu de `wsgi_pythonanywhere.py`
4. Remplace `TONUSERNAME` par ton username
5. Sauvegarde

---

## Étape 7: Configurer les fichiers statiques

Dans l'onglet **"Web"**, section **"Static files"**:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/TONUSERNAME/smile/staticfiles` |
| `/media/` | `/home/TONUSERNAME/smile/media` |

---

## Étape 8: Finaliser

Dans la console Bash:

```bash
workon smile-env
cd ~/smile

# Appliquer les migrations
python manage.py migrate --settings=smile.settings_pythonanywhere

# Collecter les fichiers statiques
python manage.py collectstatic --noinput --settings=smile.settings_pythonanywhere

# Compiler les traductions
python manage.py compilemessages --settings=smile.settings_pythonanywhere

# Créer un superuser
python manage.py createsuperuser --settings=smile.settings_pythonanywhere

# Créer les données initiales (langues, devises)
python manage.py shell --settings=smile.settings_pythonanywhere << 'EOF'
from core.models import Language, Currency

# Langues
for code, name, default in [('fr', 'Français', True), ('en', 'English', False), ('ht', 'Kreyòl Ayisyen', False)]:
    Language.objects.get_or_create(code=code, defaults={'name': name, 'is_active': True, 'is_default': default})

# Devises
for code, name, symbol, rate, default in [('EUR', 'Euro', '€', 1.0, True), ('USD', 'Dollar US', '$', 1.09, False), ('CAD', 'Dollar Canadien', 'CA$', 1.49, False), ('HTG', 'Gourde Haïtienne', 'G', 143.50, False)]:
    Currency.objects.get_or_create(code=code, defaults={'name': name, 'symbol': symbol, 'rate': rate, 'is_active': True, 'is_default': default})

print("✅ Données créées!")
EOF
```

---

## Étape 9: Lancer le site! 🎉

1. Retourne dans l'onglet **"Web"**
2. Clique le gros bouton vert **"Reload"**
3. Ton site est en ligne sur: `https://TONUSERNAME.pythonanywhere.com`

---

## 🔧 Dépannage

### Erreur 500?
```bash
# Regarde les logs
cat ~/smile/error.log
# Ou dans Web → Error log
```

### Erreur de base de données?
- Vérifie que le mot de passe MySQL est correct dans settings
- Vérifie que la base `TONUSERNAME$smile_db` existe

### Fichiers statiques cassés?
```bash
workon smile-env
cd ~/smile
python manage.py collectstatic --noinput --settings=smile.settings_pythonanywhere
```
Puis **Reload** dans l'onglet Web.

---

## 📝 Mise à jour du site

Quand tu modifies ton code:

```bash
# Si tu utilises Git
cd ~/smile
git pull

# Puis
workon smile-env
python manage.py migrate --settings=smile.settings_pythonanywhere
python manage.py collectstatic --noinput --settings=smile.settings_pythonanywhere
```

Puis **Reload** dans l'onglet Web.

---

## ✅ Checklist finale

- [ ] Compte PythonAnywhere créé
- [ ] Code uploadé dans `/home/TONUSERNAME/smile`
- [ ] Virtualenv créé et packages installés
- [ ] Base MySQL créée (`TONUSERNAME$smile_db`)
- [ ] Settings configurés avec le bon username
- [ ] WSGI configuré
- [ ] Fichiers statiques configurés
- [ ] Migrations appliquées
- [ ] Superuser créé
- [ ] Site rechargé et fonctionnel! 🎉

---

Ton site sera accessible sur: **https://TONUSERNAME.pythonanywhere.com**

Bonne chance! 🚀
