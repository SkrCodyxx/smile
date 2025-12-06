"""
Vues pour l'application core
"""
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from .models import LegalPage, SiteSettings, ContactInfo, Address, CustomField, EmailSettings


def legal_page(request, slug):
    """Affiche une page légale"""
    page = get_object_or_404(LegalPage, slug=slug, is_active=True)
    return render(request, 'core/legal_page.html', {'page': page})


def contact_page(request):
    """Page de contact avec formulaire"""
    settings = SiteSettings.get_settings()
    contacts = ContactInfo.objects.filter(is_active=True)
    addresses = Address.objects.filter(is_active=True)
    contact_fields = CustomField.objects.filter(location='contact', is_active=True)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and message:
            email_settings = EmailSettings.get_settings()
            
            if email_settings.admin_email and email_settings.send_contact_notifications:
                try:
                    from django.core.mail import EmailMessage, get_connection
                    
                    connection = get_connection(
                        host=email_settings.smtp_host,
                        port=email_settings.smtp_port,
                        username=email_settings.smtp_username,
                        password=email_settings.smtp_password,
                        use_tls=email_settings.smtp_use_tls,
                        use_ssl=email_settings.smtp_use_ssl,
                    )
                    
                    email_message = EmailMessage(
                        subject=f'[Contact] {subject or "Nouveau message"}',
                        body=f'''
Nouveau message de contact:

Nom: {name}
Email: {email}
Sujet: {subject or "Non spécifié"}

Message:
{message}
                        ''',
                        from_email=f"{email_settings.default_from_name} <{email_settings.default_from_email or email_settings.smtp_username}>",
                        to=[email_settings.admin_email],
                        reply_to=[email],
                        connection=connection,
                    )
                    email_message.send()
                except Exception as e:
                    pass  # Log error but don't show to user
            
            messages.success(request, 'Votre message a bien été envoyé. Nous vous répondrons dans les plus brefs délais.')
        else:
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
    
    return render(request, 'core/contact.html', {
        'contacts': contacts,
        'addresses': addresses,
        'contact_fields': contact_fields,
    })


def about_page(request):
    """Page À propos"""
    # Cherche si une page "about" existe
    about_content = LegalPage.objects.filter(page_type='about', is_active=True).first()
    
    return render(request, 'core/about.html', {
        'about_content': about_content,
    })


def cgv_page(request):
    """Conditions Générales de Vente"""
    cgv_content = LegalPage.objects.filter(page_type='cgv', is_active=True).first()
    return render(request, 'core/cgv.html', {
        'cgv_content': cgv_content,
    })


def legal_page_static(request):
    """Mentions légales"""
    legal_content = LegalPage.objects.filter(page_type='legal', is_active=True).first()
    return render(request, 'core/legal.html', {
        'legal_content': legal_content,
    })


def privacy_page(request):
    """Politique de confidentialité"""
    privacy_content = LegalPage.objects.filter(page_type='privacy', is_active=True).first()
    return render(request, 'core/privacy.html', {
        'privacy_content': privacy_content,
    })


def faq_page(request):
    """Foire Aux Questions"""
    faq_content = LegalPage.objects.filter(page_type='faq', is_active=True).first()
    return render(request, 'core/faq.html', {
        'faq_content': faq_content,
    })


def shipping_page(request):
    """Informations de livraison"""
    shipping_content = LegalPage.objects.filter(page_type='shipping', is_active=True).first()
    return render(request, 'core/shipping.html', {
        'shipping_content': shipping_content,
    })


def returns_page(request):
    """Politique de retour"""
    returns_content = LegalPage.objects.filter(page_type='returns', is_active=True).first()
    return render(request, 'core/returns.html', {
        'returns_content': returns_content,
    })


def set_currency(request):
    """Change la devise de l'utilisateur"""
    from django.shortcuts import redirect
    from .models import Currency
    
    if request.method == 'POST':
        currency_code = request.POST.get('currency')
        next_url = request.POST.get('next', '/')
        
        # Vérifier que la devise existe et est active
        try:
            currency = Currency.objects.get(code=currency_code, is_active=True)
            request.session['currency'] = currency.code
        except Currency.DoesNotExist:
            pass
        
        return redirect(next_url)
    
    return redirect('shop:home')
