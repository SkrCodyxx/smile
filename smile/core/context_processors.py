"""
Context processor pour rendre les paramètres du site disponibles dans tous les templates
"""
from .models import (
    SiteSettings, ContactInfo, Address, EmailSettings,
    PaymentSettings, ShippingMethod, CustomField, Banner, LegalPage, Currency, Language
)


def site_settings(request):
    """
    Ajoute tous les paramètres du site au contexte des templates
    """
    settings = SiteSettings.get_settings()
    
    # Contacts
    contacts = ContactInfo.objects.filter(is_active=True)
    header_contacts = contacts.filter(show_in_header=True)
    footer_contacts = contacts.filter(show_in_footer=True)
    primary_email = contacts.filter(contact_type='email', is_primary=True).first()
    primary_phone = contacts.filter(contact_type__in=['phone', 'mobile'], is_primary=True).first()
    
    # Adresses
    addresses = Address.objects.filter(is_active=True)
    footer_addresses = addresses.filter(show_in_footer=True)
    primary_address = addresses.filter(is_primary=True).first()
    
    # Langues actives
    languages = Language.get_active_languages() if hasattr(Language, 'get_active_languages') else []
    
    # Champs personnalisés
    custom_fields = CustomField.objects.filter(is_active=True)
    header_fields = custom_fields.filter(location='header')
    footer_fields = custom_fields.filter(location='footer')
    contact_fields = custom_fields.filter(location='contact')
    
    # Bannières actives
    from django.utils import timezone
    from django.db.models import Q
    now = timezone.now()
    
    hero_banners = Banner.objects.filter(is_active=True, banner_type='hero').filter(
        Q(start_date__isnull=True) | Q(start_date__lte=now)
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=now)
    )
    promo_banners = Banner.objects.filter(is_active=True, banner_type='promo').filter(
        Q(start_date__isnull=True) | Q(start_date__lte=now)
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=now)
    )
    announcement_banner = Banner.objects.filter(is_active=True, banner_type='announcement').filter(
        Q(start_date__isnull=True) | Q(start_date__lte=now)
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=now)
    ).first()
    
    # Pages légales
    legal_pages = LegalPage.objects.filter(is_active=True)
    footer_legal_pages = legal_pages.filter(show_in_footer=True)
    
    # Méthodes de livraison
    shipping_methods = ShippingMethod.objects.filter(is_active=True)
    
    # Paiement
    payment_settings = PaymentSettings.get_settings()
    
    # Devises
    currencies = Currency.get_active_currencies()
    current_currency = None
    
    if request:
        currency_code = request.session.get('currency')
        if currency_code:
            try:
                current_currency = Currency.objects.get(code=currency_code, is_active=True)
            except Currency.DoesNotExist:
                pass
    
    if not current_currency:
        current_currency = Currency.get_default()
    
    return {
        # Settings généraux
        'site_settings': settings,
        'site_name': settings.site_name,
        'site_slogan': settings.site_slogan,
        'site_logo': settings.logo,
        'site_favicon': settings.favicon,
        'currency_symbol': settings.currency_symbol,
        'tax_rate': settings.tax_rate,
        'free_shipping_threshold': settings.free_shipping_threshold,
        
        # Social
        'social_links': {
            'facebook': settings.facebook_url,
            'instagram': settings.instagram_url,
            'twitter': settings.twitter_url,
            'youtube': settings.youtube_url,
            'linkedin': settings.linkedin_url,
            'tiktok': settings.tiktok_url,
            'whatsapp': settings.whatsapp_number,
        },
        
        # Contacts
        'all_contacts': contacts,
        'header_contacts': header_contacts,
        'footer_contacts': footer_contacts,
        'primary_email': primary_email,
        'primary_phone': primary_phone,
        
        # Adresses
        'all_addresses': addresses,
        'footer_addresses': footer_addresses,
        'primary_address': primary_address,
        
        # Champs personnalisés
        'header_custom_fields': header_fields,
        'footer_custom_fields': footer_fields,
        'contact_custom_fields': contact_fields,
        
        # Bannières
        'hero_banners': hero_banners,
        'promo_banners': promo_banners,
        'announcement_banner': announcement_banner,
        
        # Pages
        'footer_legal_pages': footer_legal_pages,
        
        # Livraison
        'shipping_methods': shipping_methods,
        
        # Paiement
        'payment_settings': payment_settings,
        'payment_methods': payment_settings.available_methods,
        
        # Maintenance
        'maintenance_mode': settings.maintenance_mode,
        'maintenance_message': settings.maintenance_message,
        
        # Devises
        'currencies': currencies,
        'current_currency': current_currency,
        
        # Langues
        'languages': languages,
    }
