"""
Tâches CRON pour l'application Core.

Ces fonctions sont appelées automatiquement par django-crontab.
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def update_exchange_rates_job():
    """
    Tâche CRON pour mettre à jour les taux de change quotidiennement.
    
    Appelée automatiquement à 17h00 et 8h00 chaque jour.
    Utilise l'API Frankfurter (gratuite, basée sur la BCE).
    """
    from core.services.currency_updater import CurrencyUpdater
    
    start_time = datetime.now()
    logger.info(f"[CRON] Début de la mise à jour des taux de change - {start_time}")
    print(f"[{start_time}] Début de la mise à jour des taux de change...")
    
    try:
        updater = CurrencyUpdater(api_name='frankfurter')
        
        # Forcer la récupération (ignorer le cache)
        rates = updater.fetch_rates(force=True)
        
        if rates:
            # Mettre à jour la base de données
            updated_count = updater.update_database_rates(rates)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            msg = f"[CRON] Mise à jour terminée: {updated_count} devise(s) mise(s) à jour en {duration:.2f}s"
            logger.info(msg)
            print(f"[{end_time}] {msg}")
            
            return updated_count
        else:
            logger.warning("[CRON] Aucun taux récupéré depuis l'API")
            print(f"[{datetime.now()}] ATTENTION: Aucun taux récupéré")
            return 0
            
    except Exception as e:
        logger.error(f"[CRON] Erreur lors de la mise à jour des taux: {e}")
        print(f"[{datetime.now()}] ERREUR: {e}")
        raise


def cleanup_old_sessions_job():
    """
    Tâche CRON optionnelle pour nettoyer les anciennes sessions.
    """
    from django.core.management import call_command
    
    logger.info("[CRON] Nettoyage des anciennes sessions...")
    call_command('clearsessions')
    logger.info("[CRON] Sessions nettoyées")
