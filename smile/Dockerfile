FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installer les dépendances système (incluant cron et gettext pour i18n)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    cron \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le projet
COPY . .

# Compiler les traductions
RUN python manage.py compilemessages || true

# Collecter les fichiers statiques
RUN python manage.py collectstatic --noinput

# Créer le fichier de log pour cron
RUN touch /var/log/cron_exchange_rates.log && chmod 666 /var/log/cron_exchange_rates.log

# Rendre le script d'entrée exécutable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

# Utiliser le script d'entrée
ENTRYPOINT ["/entrypoint.sh"]

# Script de démarrage
CMD ["sh", "-c", "python manage.py migrate && python manage.py loaddata initial_settings --ignorenonexistent || true && gunicorn smile.wsgi:application --bind 0.0.0.0:8000 --workers 3"]
