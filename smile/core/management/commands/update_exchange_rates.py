"""
Commande Django pour mettre à jour les taux de change.

Usage:
    python manage.py update_exchange_rates
    python manage.py update_exchange_rates --api frankfurter
    python manage.py update_exchange_rates --api exchangerate --api-key YOUR_KEY
    python manage.py update_exchange_rates --force
"""
from django.core.management.base import BaseCommand
from core.services.currency_updater import CurrencyUpdater


class Command(BaseCommand):
    help = 'Met à jour les taux de change depuis une API externe'

    def add_arguments(self, parser):
        parser.add_argument(
            '--api',
            type=str,
            default='frankfurter',
            choices=['frankfurter', 'exchangerate', 'fixer'],
            help='API à utiliser (défaut: frankfurter - gratuit et illimité)'
        )
        parser.add_argument(
            '--api-key',
            type=str,
            default=None,
            help='Clé API (requise pour exchangerate et fixer)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la mise à jour même si le cache est valide'
        )
        parser.add_argument(
            '--show-rates',
            action='store_true',
            help='Afficher tous les taux récupérés'
        )

    def handle(self, *args, **options):
        api_name = options['api']
        api_key = options['api_key']
        force = options['force']
        show_rates = options['show_rates']

        self.stdout.write(f"🔄 Récupération des taux de change via {api_name}...")
        
        try:
            updater = CurrencyUpdater(api_name=api_name, api_key=api_key)
            
            # Récupérer les taux
            rates = updater.fetch_rates(force=force)
            
            if not rates:
                self.stdout.write(self.style.ERROR("❌ Aucun taux récupéré"))
                return
            
            self.stdout.write(self.style.SUCCESS(f"✅ {len(rates)} taux récupérés"))
            
            # Afficher les taux si demandé
            if show_rates:
                self.stdout.write("\n📊 Taux de change (base EUR):")
                for code in sorted(rates.keys()):
                    self.stdout.write(f"   {code}: {rates[code]}")
            
            # Mettre à jour la base de données
            self.stdout.write("\n💾 Mise à jour de la base de données...")
            updated = updater.update_database_rates(rates)
            
            if updated > 0:
                self.stdout.write(self.style.SUCCESS(f"✅ {updated} devise(s) mise(s) à jour"))
            else:
                self.stdout.write("ℹ️  Aucune mise à jour nécessaire (taux identiques)")
            
            # Afficher les devises du site
            from core.models import Currency
            self.stdout.write("\n💱 Devises configurées sur le site:")
            for currency in Currency.objects.filter(is_active=True).order_by('-is_default', 'code'):
                default_marker = " ⭐" if currency.is_default else ""
                self.stdout.write(
                    f"   {currency.code}: {currency.symbol} - "
                    f"Taux: {currency.exchange_rate}{default_marker}"
                )
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erreur: {e}"))
            raise
