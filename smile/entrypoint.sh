#!/bin/bash
set -e

echo "🚀 Démarrage de Smile Shop..."

# Attendre que la base de données soit prête
echo "⏳ Attente de la base de données..."
sleep 5

# Appliquer les migrations
echo "📦 Application des migrations..."
python manage.py migrate --noinput

# Configurer les tâches CRON
echo "⏰ Configuration des tâches CRON..."
python manage.py crontab remove 2>/dev/null || true
python manage.py crontab add
python manage.py crontab show

# Démarrer le service cron en arrière-plan
echo "🔄 Démarrage du service CRON..."
service cron start

# Mise à jour initiale des taux de change
echo "💱 Mise à jour initiale des taux de change..."
python manage.py update_exchange_rates || echo "⚠️ Impossible de mettre à jour les taux (pas de connexion internet?)"

# Démarrer gunicorn
echo "🌐 Démarrage de Gunicorn..."
exec gunicorn smile.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
