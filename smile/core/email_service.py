"""
Service d'envoi d'emails - Smile Shop
=====================================
Gère tous les emails transactionnels du site
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def get_email_context(extra_context=None):
    """Contexte de base pour tous les emails"""
    context = {
        'site_name': getattr(settings, 'SITE_NAME', 'Smile Shop'),
        'site_url': getattr(settings, 'SITE_URL', 'https://smile.pythonanywhere.com'),
        'current_year': timezone.now().year,
    }
    if extra_context:
        context.update(extra_context)
    return context


def send_email(to_email, subject, template_name, context, reply_to=None):
    """
    Fonction générique pour envoyer un email HTML
    """
    try:
        full_context = get_email_context(context)
        html_content = render_to_string(f'emails/{template_name}.html', full_context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email] if isinstance(to_email, str) else to_email,
            reply_to=[reply_to] if reply_to else None,
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        logger.info(f"Email '{subject}' envoyé à {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur envoi email '{subject}': {str(e)}")
        return False


# =============================================================================
# EMAILS COMMANDES
# =============================================================================

def send_order_confirmation(order):
    """Email de confirmation de commande"""
    return send_email(
        to_email=order.email,
        subject=f'Confirmation de commande #{order.order_number} - Smile Shop',
        template_name='order_confirmation',
        context={'order': order}
    )


def send_order_shipped(order, tracking_number=None):
    """Email quand la commande est expédiée"""
    return send_email(
        to_email=order.email,
        subject=f'Votre commande #{order.order_number} a été expédiée!',
        template_name='order_shipped',
        context={'order': order, 'tracking_number': tracking_number}
    )


def send_order_delivered(order):
    """Email quand la commande est livrée"""
    return send_email(
        to_email=order.email,
        subject=f'Votre commande #{order.order_number} a été livrée!',
        template_name='order_delivered',
        context={'order': order, 'delivery_date': timezone.now()}
    )


def send_order_cancelled(order, reason=None):
    """Email quand la commande est annulée"""
    return send_email(
        to_email=order.email,
        subject=f'Commande #{order.order_number} annulée',
        template_name='order_cancelled',
        context={'order': order, 'reason': reason}
    )


# =============================================================================
# EMAILS PAIEMENT
# =============================================================================

def send_payment_confirmed(order, transaction_id=None, payment_method=None):
    """Email de confirmation de paiement"""
    return send_email(
        to_email=order.email,
        subject=f'Paiement confirmé - Commande #{order.order_number}',
        template_name='payment_confirmed',
        context={
            'order': order,
            'transaction_id': transaction_id,
            'payment_method': payment_method,
            'payment_date': timezone.now()
        }
    )


def send_payment_failed(order, error_message=None):
    """Email quand le paiement échoue"""
    return send_email(
        to_email=order.email,
        subject=f'Échec du paiement - Commande #{order.order_number}',
        template_name='payment_failed',
        context={'order': order, 'error_message': error_message}
    )


def send_refund_processed(order, refund_amount=None, refund_reason=None):
    """Email quand un remboursement est effectué"""
    return send_email(
        to_email=order.email,
        subject=f'Remboursement effectué - Commande #{order.order_number}',
        template_name='refund_processed',
        context={
            'order': order,
            'refund_amount': refund_amount or order.total,
            'refund_reason': refund_reason
        }
    )


# =============================================================================
# EMAILS UTILISATEUR
# =============================================================================

def send_welcome_email(user):
    """Email de bienvenue aux nouveaux utilisateurs"""
    return send_email(
        to_email=user.email,
        subject=f'Bienvenue sur Smile Shop, {user.first_name or user.username}!',
        template_name='welcome',
        context={'user': user}
    )


def send_password_reset(user, reset_url):
    """Email de réinitialisation de mot de passe"""
    return send_email(
        to_email=user.email,
        subject='Réinitialisation de votre mot de passe - Smile Shop',
        template_name='password_reset',
        context={'user': user, 'reset_url': reset_url}
    )


# =============================================================================
# EMAILS CONTACT
# =============================================================================

def send_contact_notification(name, email, subject, message):
    """Notification quand quelqu'un utilise le formulaire de contact"""
    admin_email = None
    admins = getattr(settings, 'ADMINS', [])
    if admins:
        admin_email = admins[0][1]
    else:
        admin_email = getattr(settings, 'EMAIL_HOST_USER', None)
    
    if not admin_email:
        logger.warning("Pas d'email admin configuré pour les notifications contact")
        return False
    
    return send_email(
        to_email=admin_email,
        subject=f'[Contact Smile Shop] {subject}',
        template_name='contact_notification',
        context={'name': name, 'email': email, 'subject': subject, 'message': message},
        reply_to=email
    )


# =============================================================================
# EMAILS PRODUITS
# =============================================================================

def send_back_in_stock(user, product):
    """Email quand un produit est de retour en stock"""
    return send_email(
        to_email=user.email,
        subject=f'{product.name} est de retour en stock!',
        template_name='back_in_stock',
        context={'user': user, 'product': product}
    )


def send_cart_abandoned(user, cart_items, cart_total, discount_code=None, discount_percent=None):
    """Email de rappel panier abandonné"""
    return send_email(
        to_email=user.email,
        subject='Vous avez oublié quelque chose dans votre panier!',
        template_name='cart_abandoned',
        context={
            'user': user,
            'cart_items': cart_items,
            'cart_total': cart_total,
            'discount_code': discount_code,
            'discount_percent': discount_percent
        }
    )


# =============================================================================
# EMAILS FACTURE
# =============================================================================

def send_invoice(invoice):
    """Email avec la facture"""
    return send_email(
        to_email=invoice.order.email,
        subject=f'Facture {invoice.invoice_number} - Smile Shop',
        template_name='invoice',
        context={'invoice': invoice}
    )


# =============================================================================
# EMAILS NEWSLETTER
# =============================================================================

def send_newsletter(subscriber, newsletter_title, newsletter_content, 
                   featured_products=None, promo_code=None, promo_percent=None, promo_expiry=None):
    """Email newsletter"""
    return send_email(
        to_email=subscriber.email if hasattr(subscriber, 'email') else subscriber,
        subject=newsletter_title,
        template_name='newsletter',
        context={
            'subscriber': subscriber,
            'newsletter_title': newsletter_title,
            'newsletter_content': newsletter_content,
            'featured_products': featured_products,
            'promo_code': promo_code,
            'promo_percent': promo_percent,
            'promo_expiry': promo_expiry
        }
    )


# =============================================================================
# EMAILS ADMIN
# =============================================================================

def send_new_order_admin(order):
    """Notification admin pour nouvelle commande"""
    admin_email = None
    admins = getattr(settings, 'ADMINS', [])
    if admins:
        admin_email = admins[0][1]
    
    if not admin_email:
        return False
    
    subject = f'🛒 Nouvelle commande #{order.order_number} - {order.total} EUR'
    message = f"""
    Nouvelle commande reçue!
    
    Numéro: {order.order_number}
    Client: {order.first_name} {order.last_name}
    Email: {order.email}
    Total: {order.total} EUR
    
    Voir dans l'admin: {getattr(settings, 'SITE_URL', '')}/admin/invoicing/order/{order.id}/
    """
    
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [admin_email])
        return True
    except Exception as e:
        logger.error(f"Erreur notification admin nouvelle commande: {str(e)}")
        return False
