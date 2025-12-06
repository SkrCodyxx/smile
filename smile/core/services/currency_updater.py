"""
Service de mise à jour des taux de change en temps réel.

APIs gratuites supportées:
1. exchangerate-api.com (1500 requêtes/mois gratuit)
2. frankfurter.app (gratuit, illimité, basé sur BCE)
3. fixer.io (100 requêtes/mois gratuit)

La BCE (Banque Centrale Européenne) publie les taux chaque jour vers 16h CET.
"""
import logging
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Optional
import requests
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class CurrencyUpdater:
    """
    Service pour récupérer et mettre à jour les taux de change.
    """
    
    # APIs disponibles (par ordre de préférence)
    APIS = {
        'frankfurter': {
            'url': 'https://api.frankfurter.app/latest',
            'params': {'from': 'EUR'},
            'free': True,
            'limit': 'Illimité',
            'source': 'Banque Centrale Européenne',
        },
        'exchangerate': {
            'url': 'https://v6.exchangerate-api.com/v6/{api_key}/latest/EUR',
            'free': True,
            'limit': '1500/mois',
            'source': 'ExchangeRate-API',
        },
        'fixer': {
            'url': 'http://data.fixer.io/api/latest',
            'params': {'access_key': '{api_key}', 'base': 'EUR'},
            'free': True,
            'limit': '100/mois',
            'source': 'Fixer.io',
        },
    }
    
    # Cache des taux (durée: 1 heure)
    CACHE_KEY = 'currency_exchange_rates'
    CACHE_TIMEOUT = 3600  # 1 heure
    
    def __init__(self, api_name: str = 'frankfurter', api_key: str = None):
        """
        Initialise le service.
        
        Args:
            api_name: Nom de l'API à utiliser ('frankfurter', 'exchangerate', 'fixer')
            api_key: Clé API (requise pour exchangerate et fixer)
        """
        self.api_name = api_name
        self.api_key = api_key or getattr(settings, 'EXCHANGE_RATE_API_KEY', None)
        self.api_config = self.APIS.get(api_name, self.APIS['frankfurter'])
    
    def fetch_rates(self, force: bool = False) -> Dict[str, Decimal]:
        """
        Récupère les taux de change depuis l'API.
        
        Args:
            force: Ignorer le cache et forcer une nouvelle requête
            
        Returns:
            Dict avec les codes de devise et leurs taux par rapport à EUR
        """
        # Vérifier le cache
        if not force:
            cached_rates = cache.get(self.CACHE_KEY)
            if cached_rates:
                logger.info("Taux de change récupérés depuis le cache")
                return cached_rates
        
        rates = {}
        
        try:
            if self.api_name == 'frankfurter':
                rates = self._fetch_frankfurter()
            elif self.api_name == 'exchangerate':
                rates = self._fetch_exchangerate()
            elif self.api_name == 'fixer':
                rates = self._fetch_fixer()
            else:
                # Fallback sur Frankfurter
                rates = self._fetch_frankfurter()
            
            if rates:
                # Ajouter EUR = 1
                rates['EUR'] = Decimal('1.0')
                
                # Mettre en cache
                cache.set(self.CACHE_KEY, rates, self.CACHE_TIMEOUT)
                logger.info(f"Taux de change mis à jour: {len(rates)} devises")
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des taux: {e}")
            
            # Essayer un fallback
            if self.api_name != 'frankfurter':
                logger.info("Tentative de fallback sur Frankfurter...")
                try:
                    rates = self._fetch_frankfurter()
                    if rates:
                        rates['EUR'] = Decimal('1.0')
                        cache.set(self.CACHE_KEY, rates, self.CACHE_TIMEOUT)
                except:
                    pass
        
        return rates
    
    def _fetch_frankfurter(self) -> Dict[str, Decimal]:
        """
        Récupère les taux depuis Frankfurter (gratuit, basé sur BCE).
        """
        url = 'https://api.frankfurter.app/latest'
        params = {'from': 'EUR'}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        rates = {}
        
        for code, rate in data.get('rates', {}).items():
            rates[code] = Decimal(str(rate))
        
        logger.info(f"Frankfurter: {len(rates)} taux récupérés (date: {data.get('date')})")
        return rates
    
    def _fetch_exchangerate(self) -> Dict[str, Decimal]:
        """
        Récupère les taux depuis ExchangeRate-API.
        Nécessite une clé API gratuite.
        """
        if not self.api_key:
            raise ValueError("Clé API requise pour ExchangeRate-API")
        
        url = f'https://v6.exchangerate-api.com/v6/{self.api_key}/latest/EUR'
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('result') != 'success':
            raise ValueError(f"Erreur API: {data.get('error-type')}")
        
        rates = {}
        for code, rate in data.get('conversion_rates', {}).items():
            rates[code] = Decimal(str(rate))
        
        logger.info(f"ExchangeRate-API: {len(rates)} taux récupérés")
        return rates
    
    def _fetch_fixer(self) -> Dict[str, Decimal]:
        """
        Récupère les taux depuis Fixer.io.
        Nécessite une clé API gratuite.
        """
        if not self.api_key:
            raise ValueError("Clé API requise pour Fixer.io")
        
        url = 'http://data.fixer.io/api/latest'
        params = {
            'access_key': self.api_key,
            'base': 'EUR',  # Note: base EUR gratuit uniquement
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('success'):
            raise ValueError(f"Erreur API: {data.get('error', {}).get('info')}")
        
        rates = {}
        for code, rate in data.get('rates', {}).items():
            rates[code] = Decimal(str(rate))
        
        logger.info(f"Fixer.io: {len(rates)} taux récupérés")
        return rates
    
    def update_database_rates(self, rates: Dict[str, Decimal] = None) -> int:
        """
        Met à jour les taux de change dans la base de données.
        
        Returns:
            Nombre de devises mises à jour
        """
        from core.models import Currency
        
        if rates is None:
            rates = self.fetch_rates()
        
        if not rates:
            logger.warning("Aucun taux à mettre à jour")
            return 0
        
        updated = 0
        
        for currency in Currency.objects.filter(is_active=True):
            if currency.code in rates:
                old_rate = currency.exchange_rate
                new_rate = rates[currency.code]
                
                if old_rate != new_rate:
                    currency.exchange_rate = new_rate
                    currency.save(update_fields=['exchange_rate', 'updated_at'])
                    logger.info(f"{currency.code}: {old_rate} -> {new_rate}")
                    updated += 1
        
        return updated
    
    def get_rate(self, currency_code: str) -> Optional[Decimal]:
        """
        Récupère le taux pour une devise spécifique.
        """
        rates = self.fetch_rates()
        return rates.get(currency_code.upper())
    
    def convert(self, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        """
        Convertit un montant d'une devise à une autre.
        """
        rates = self.fetch_rates()
        
        from_rate = rates.get(from_currency.upper(), Decimal('1'))
        to_rate = rates.get(to_currency.upper(), Decimal('1'))
        
        # Convertir via EUR
        amount_in_eur = Decimal(str(amount)) / from_rate
        return amount_in_eur * to_rate


def update_exchange_rates(api_name: str = 'frankfurter', api_key: str = None) -> int:
    """
    Fonction utilitaire pour mettre à jour les taux de change.
    Peut être appelée depuis une tâche Celery ou une commande manage.py.
    
    Returns:
        Nombre de devises mises à jour
    """
    updater = CurrencyUpdater(api_name=api_name, api_key=api_key)
    return updater.update_database_rates()


def get_live_rate(currency_code: str) -> Optional[Decimal]:
    """
    Récupère le taux de change en direct pour une devise.
    """
    updater = CurrencyUpdater()
    return updater.get_rate(currency_code)
