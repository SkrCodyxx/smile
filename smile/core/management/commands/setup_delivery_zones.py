"""
Commande pour créer les zones de livraison par défaut pour Haïti
"""
from django.core.management.base import BaseCommand
from core.models import DeliveryZone


class Command(BaseCommand):
    help = 'Crée les zones de livraison par défaut pour Haïti'

    def handle(self, *args, **options):
        zones_data = [
            {
                'name': 'Zone 1 - Port-au-Prince Centre',
                'areas': 'Port-au-Prince, Pétion-Ville, Delmas',
                'delivery_time_min': 0,
                'delivery_time_max': 1,
                'delivery_cost': 0,
                'cost_note': 'Contactez-nous',
                'order': 1,
                'is_active': True,
                'notes': 'Zone principale - Livraison rapide',
            },
            {
                'name': 'Zone 2 - Périphérie',
                'areas': 'Carrefour, Tabarre, Croix-des-Bouquets',
                'delivery_time_min': 1,
                'delivery_time_max': 2,
                'delivery_cost': 0,
                'cost_note': 'Contactez-nous',
                'order': 2,
                'is_active': True,
                'notes': '',
            },
            {
                'name': 'Zone 3 - Grandes Villes',
                'areas': 'Cap-Haïtien, Les Cayes, Jacmel',
                'delivery_time_min': 2,
                'delivery_time_max': 5,
                'delivery_cost': 0,
                'cost_note': 'Contactez-nous',
                'order': 3,
                'is_active': True,
                'notes': '',
            },
            {
                'name': 'Zone 4 - Autres Régions',
                'areas': "Autres régions d'Haïti",
                'delivery_time_min': 3,
                'delivery_time_max': 7,
                'delivery_cost': 0,
                'cost_note': 'Contactez-nous',
                'order': 4,
                'is_active': True,
                'notes': 'Délais variables selon la localisation',
            },
        ]

        created_count = 0
        for zone_data in zones_data:
            zone, created = DeliveryZone.objects.get_or_create(
                name=zone_data['name'],
                defaults=zone_data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Zone créée: {zone.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'⏭️  Zone existe déjà: {zone.name}'))

        self.stdout.write(self.style.SUCCESS(f'\n🎉 {created_count} zone(s) créée(s) avec succès!'))
