from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from shop.models import Product
import uuid
from datetime import date, timedelta


class Order(models.Model):
    """Commande"""
    STATUS_CHOICES = [
        ('pending', '⏳ En attente'),
        ('confirmed', '✅ Confirmée'),
        ('processing', '📦 En préparation'),
        ('shipped', '🚚 Expédiée'),
        ('delivered', '✔️ Livrée'),
        ('cancelled', '❌ Annulée'),
        ('refunded', '💰 Remboursée'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', '⏳ En attente'),
        ('paid', '✅ Payée'),
        ('failed', '❌ Échoué'),
        ('refunded', '💰 Remboursée'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cod', '💵 Paiement à la livraison'),
        ('moncash', '📱 MonCash'),
        ('natcash', '📱 NatCash'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField('N° Commande', max_length=50, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders',
                             verbose_name='Client')
    
    status = models.CharField('Statut', max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField('Paiement', max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField('Méthode de paiement', max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')
    payment_reference = models.CharField('Référence paiement', max_length=100, blank=True,
                                         help_text='Numéro de transaction MonCash/NatCash')
    
    # Montants
    subtotal = models.DecimalField('Sous-total', max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField('TVA', max_digits=10, decimal_places=2, default=0)
    shipping_amount = models.DecimalField('Frais de port', max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField('Réduction', max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField('Total', max_digits=10, decimal_places=2)
    
    # Adresses
    shipping_address = models.TextField('Adresse de livraison', blank=True)
    billing_address = models.TextField('Adresse de facturation', blank=True)
    
    # Infos
    notes = models.TextField('Notes', blank=True)
    tracking_number = models.CharField('N° de suivi', max_length=100, blank=True)
    
    # Dates
    shipped_at = models.DateTimeField('Expédiée le', null=True, blank=True)
    delivered_at = models.DateTimeField('Livrée le', null=True, blank=True)
    created_at = models.DateTimeField('Créée le', auto_now_add=True)
    updated_at = models.DateTimeField('Modifiée le', auto_now=True)

    class Meta:
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering = ['-created_at']

    def __str__(self):
        return f"Commande {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Générer un numéro de commande avec les paramètres du site
            try:
                from core.models import SiteSettings
                settings = SiteSettings.get_settings()
                self.order_number = settings.get_next_order_number()
            except:
                # Fallback
                last_order = Order.objects.order_by('-created_at').first()
                if last_order and last_order.order_number:
                    try:
                        last_num = int(last_order.order_number.split('-')[1])
                        new_num = last_num + 1
                    except:
                        new_num = 1
                else:
                    new_num = 1
                self.order_number = f"CMD-{new_num:06d}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('invoicing:order_detail', kwargs={'order_id': self.id})


class OrderItem(models.Model):
    """Article de commande"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField('Produit', max_length=255)
    product_sku = models.CharField('SKU', max_length=100, blank=True)
    quantity = models.PositiveIntegerField('Quantité')
    unit_price = models.DecimalField('Prix unitaire', max_digits=10, decimal_places=2)
    total_price = models.DecimalField('Total', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Article de commande'
        verbose_name_plural = 'Articles de commande'

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"


class Invoice(models.Model):
    """Facture"""
    STATUS_CHOICES = [
        ('draft', '📝 Brouillon'),
        ('sent', '📧 Envoyée'),
        ('paid', '✅ Payée'),
        ('overdue', '⚠️ En retard'),
        ('cancelled', '❌ Annulée'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField('N° Facture', max_length=50, unique=True, blank=True)
    order = models.OneToOneField(Order, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='invoice', verbose_name='Commande')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='invoices',
                             verbose_name='Client')
    
    status = models.CharField('Statut', max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Dates
    issue_date = models.DateField('Date d\'émission', default=date.today)
    due_date = models.DateField('Date d\'échéance')
    
    # Montants
    subtotal = models.DecimalField('Sous-total HT', max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField('Taux TVA (%)', max_digits=5, decimal_places=2, default=20.00)
    tax_amount = models.DecimalField('Montant TVA', max_digits=10, decimal_places=2)
    total = models.DecimalField('Total TTC', max_digits=10, decimal_places=2)
    
    # Infos
    notes = models.TextField('Notes', blank=True)
    payment_terms = models.TextField('Conditions de paiement', blank=True)
    
    paid_at = models.DateTimeField('Payée le', null=True, blank=True)
    created_at = models.DateTimeField('Créée le', auto_now_add=True)
    updated_at = models.DateTimeField('Modifiée le', auto_now=True)

    class Meta:
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'
        ordering = ['-created_at']

    def __str__(self):
        return f"Facture {self.invoice_number}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Générer un numéro de facture avec les paramètres du site
            try:
                from core.models import SiteSettings
                settings = SiteSettings.get_settings()
                self.invoice_number = settings.get_next_invoice_number()
            except:
                # Fallback
                year = date.today().year
                last_invoice = Invoice.objects.filter(
                    invoice_number__startswith=f"FAC-{year}"
                ).order_by('-created_at').first()
                
                if last_invoice and last_invoice.invoice_number:
                    try:
                        last_num = int(last_invoice.invoice_number.split('-')[2])
                        new_num = last_num + 1
                    except:
                        new_num = 1
                else:
                    new_num = 1
                self.invoice_number = f"FAC-{year}-{new_num:05d}"
        
        if not self.due_date:
            self.due_date = self.issue_date + timedelta(days=30)
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('invoicing:invoice_detail', kwargs={'invoice_id': self.id})

    @property
    def is_overdue(self):
        return self.status not in ['paid', 'cancelled'] and date.today() > self.due_date


class InvoiceItem(models.Model):
    """Ligne de facture"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField('Description', max_length=255)
    quantity = models.PositiveIntegerField('Quantité', default=1)
    unit_price = models.DecimalField('Prix unitaire HT', max_digits=10, decimal_places=2)
    total_price = models.DecimalField('Total HT', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Ligne de facture'
        verbose_name_plural = 'Lignes de facture'

    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Customer(models.Model):
    """Client (infos supplémentaires)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    company = models.CharField('Entreprise', max_length=255, blank=True)
    phone = models.CharField('Téléphone', max_length=20, blank=True)
    address = models.TextField('Adresse', blank=True)
    city = models.CharField('Ville', max_length=100, blank=True)
    postal_code = models.CharField('Code postal', max_length=20, blank=True)
    country = models.CharField('Pays', max_length=100, default='France')
    siret = models.CharField('SIRET', max_length=20, blank=True)
    vat_number = models.CharField('N° TVA', max_length=30, blank=True)
    notes = models.TextField('Notes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Profil client'
        verbose_name_plural = 'Profils clients'

    def __str__(self):
        if self.company:
            return f"{self.company} ({self.user.email})"
        return self.user.email
