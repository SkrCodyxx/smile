"""
Template tags pour le formatage des prix et la gestion des devises
"""
from django import template
from django.utils.safestring import mark_safe
from decimal import Decimal

register = template.Library()


@register.simple_tag(takes_context=True)
def price(context, amount, show_converted=True):
    """
    Affiche un prix formaté dans la devise sélectionnée par l'utilisateur
    
    Usage: {% price product.price %}
    """
    if amount is None:
        return ''
    
    request = context.get('request')
    currency = get_current_currency(request)
    
    if currency:
        return mark_safe(currency.format_price(amount))
    else:
        # Fallback: format simple en EUR
        return f"{Decimal(str(amount)):.2f} €"


@register.filter
def format_price(amount, currency=None):
    """
    Filtre pour formater un prix avec conversion automatique.
    
    IMPORTANT: Ce filtre nécessite que la devise soit passée via le context processor.
    Dans les templates, utilisez: {{ product.price|format_price:current_currency }}
    
    Usage simple (sans conversion): {{ product.price|format_price }}
    Usage avec devise: {{ product.price|format_price:current_currency }}
    """
    if amount is None:
        return ''
    
    from decimal import Decimal
    
    if currency and hasattr(currency, 'format_price'):
        # format_price fait déjà la conversion, pas besoin de convert_from_base ici
        return currency.format_price(amount)
    
    # Fallback: format simple en EUR
    try:
        value = Decimal(str(amount))
        return f"{value:.2f} €"
    except:
        return f"{amount} €"


@register.simple_tag(takes_context=True)
def currency_symbol(context):
    """
    Retourne le symbole de la devise actuelle
    
    Usage: {% currency_symbol %}
    """
    request = context.get('request')
    currency = get_current_currency(request)
    
    if currency:
        return currency.symbol
    return '€'


@register.simple_tag(takes_context=True)
def currency_code(context):
    """
    Retourne le code de la devise actuelle
    
    Usage: {% currency_code %}
    """
    request = context.get('request')
    currency = get_current_currency(request)
    
    if currency:
        return currency.code
    return 'EUR'


@register.inclusion_tag('core/includes/currency_selector.html', takes_context=True)
def currency_selector(context):
    """
    Affiche le sélecteur de devise
    
    Usage: {% currency_selector %}
    """
    from core.models import Currency
    
    request = context.get('request')
    current_currency = get_current_currency(request)
    currencies = Currency.get_active_currencies()
    
    return {
        'currencies': currencies,
        'current_currency': current_currency,
        'request': request,
    }


@register.simple_tag(takes_context=True)
def convert_price(context, amount, to_currency_code=None):
    """
    Convertit un prix vers une devise spécifique
    
    Usage: {% convert_price product.price 'USD' %}
    """
    if amount is None:
        return Decimal('0')
    
    from core.models import Currency
    
    if to_currency_code:
        try:
            currency = Currency.objects.get(code=to_currency_code, is_active=True)
            return currency.convert_from_base(amount)
        except Currency.DoesNotExist:
            pass
    
    request = context.get('request')
    currency = get_current_currency(request)
    
    if currency:
        return currency.convert_from_base(amount)
    
    return Decimal(str(amount))


def get_current_currency(request):
    """
    Récupère la devise actuellement sélectionnée par l'utilisateur
    """
    from core.models import Currency
    
    if not request:
        return Currency.get_default()
    
    # Vérifier la session
    currency_code = request.session.get('currency')
    
    if currency_code:
        try:
            return Currency.objects.get(code=currency_code, is_active=True)
        except Currency.DoesNotExist:
            pass
    
    # Retourner la devise par défaut
    return Currency.get_default()


@register.filter
def multiply(value, arg):
    """Multiplie une valeur"""
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except:
        return value
