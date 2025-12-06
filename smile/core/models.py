"""
Modèles de configuration du site - Tout est gérable depuis l'admin
"""
from django.db import models
from django.core.cache import cache
import uuid


class SiteSettings(models.Model):
    """
    Configuration générale du site - Singleton
    Une seule instance pour tout le site
    """
    # Informations de base
    site_name = models.CharField('Nom du site', max_length=200, default='Smile Shop')
    site_slogan = models.CharField('Slogan', max_length=500, blank=True)
    site_description = models.TextField('Description du site', blank=True, 
                                        help_text='Description pour le SEO')
    logo = models.ImageField('Logo', upload_to='site/', blank=True, null=True)
    favicon = models.ImageField('Favicon', upload_to='site/', blank=True, null=True)
    
    # Informations légales
    company_name = models.CharField('Raison sociale', max_length=200, blank=True)
    siret = models.CharField('SIRET', max_length=20, blank=True)
    tva_number = models.CharField('N° TVA', max_length=30, blank=True)
    rcs = models.CharField('RCS', max_length=100, blank=True)
    capital = models.CharField('Capital social', max_length=50, blank=True)
    
    # Réseaux sociaux
    facebook_url = models.URLField('Facebook', blank=True)
    instagram_url = models.URLField('Instagram', blank=True)
    twitter_url = models.URLField('Twitter/X', blank=True)
    youtube_url = models.URLField('YouTube', blank=True)
    linkedin_url = models.URLField('LinkedIn', blank=True)
    tiktok_url = models.URLField('TikTok', blank=True)
    whatsapp_number = models.CharField('WhatsApp', max_length=20, blank=True)
    
    # SEO
    meta_title = models.CharField('Titre SEO', max_length=200, blank=True)
    meta_description = models.TextField('Meta description', blank=True)
    meta_keywords = models.TextField('Mots-clés SEO', blank=True)
    google_analytics_id = models.CharField('Google Analytics ID', max_length=50, blank=True)
    facebook_pixel_id = models.CharField('Facebook Pixel ID', max_length=50, blank=True)
    
    # Paramètres boutique
    currency = models.CharField('Devise', max_length=3, default='EUR')
    currency_symbol = models.CharField('Symbole devise', max_length=5, default='€')
    tax_rate = models.DecimalField('Taux TVA (%)', max_digits=5, decimal_places=2, default=20)
    shipping_cost = models.DecimalField('Frais de port', max_digits=10, decimal_places=2, default=5.99)
    free_shipping_threshold = models.DecimalField('Livraison gratuite dès', max_digits=10, decimal_places=2, default=50)
    
    # Numérotation
    order_prefix = models.CharField('Préfixe commandes', max_length=10, default='CMD')
    order_next_number = models.PositiveIntegerField('Prochain n° commande', default=1)
    invoice_prefix = models.CharField('Préfixe factures', max_length=10, default='FAC')
    invoice_next_number = models.PositiveIntegerField('Prochain n° facture', default=1)
    product_sku_prefix = models.CharField('Préfixe SKU produits', max_length=10, default='PRD')
    product_next_number = models.PositiveIntegerField('Prochain n° produit', default=1)
    
    # Options
    maintenance_mode = models.BooleanField('Mode maintenance', default=False)
    maintenance_message = models.TextField('Message maintenance', blank=True,
                                           default='Le site est en maintenance. Revenez bientôt!')
    allow_guest_checkout = models.BooleanField('Commande sans compte', default=False)
    reviews_require_approval = models.BooleanField('Avis nécessitent approbation', default=True)
    show_stock_quantity = models.BooleanField('Afficher quantité en stock', default=True)
    low_stock_threshold = models.PositiveIntegerField('Seuil stock bas par défaut', default=10)
    
    # Horaires d'ouverture
    opening_hours = models.TextField('Horaires d\'ouverture', blank=True,
                                     help_text='Ex: Lun-Ven: 9h-18h, Sam: 10h-16h')
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuration du site'
        verbose_name_plural = 'Configuration du site'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'une seule instance
        self.pk = 1
        super().save(*args, **kwargs)
        # Invalider le cache
        cache.delete('site_settings')

    @classmethod
    def get_settings(cls):
        """Récupère les paramètres du site (avec cache)"""
        settings = cache.get('site_settings')
        if not settings:
            settings, created = cls.objects.get_or_create(pk=1)
            cache.set('site_settings', settings, 3600)  # Cache 1h
        return settings

    def get_next_order_number(self):
        """Génère le prochain numéro de commande"""
        number = f"{self.order_prefix}-{self.order_next_number:06d}"
        self.order_next_number += 1
        self.save()
        return number

    def get_next_invoice_number(self):
        """Génère le prochain numéro de facture"""
        from datetime import datetime
        year = datetime.now().year
        number = f"{self.invoice_prefix}-{year}-{self.invoice_next_number:05d}"
        self.invoice_next_number += 1
        self.save()
        return number

    def get_next_sku(self):
        """Génère le prochain SKU produit"""
        sku = f"{self.product_sku_prefix}-{self.product_next_number:06d}"
        self.product_next_number += 1
        self.save()
        return sku


class ContactInfo(models.Model):
    """
    Informations de contact - Multiples entrées possibles
    """
    CONTACT_TYPES = [
        ('email', '📧 Email'),
        ('phone', '📞 Téléphone'),
        ('mobile', '📱 Mobile'),
        ('fax', '📠 Fax'),
        ('whatsapp', '💬 WhatsApp'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact_type = models.CharField('Type', max_length=20, choices=CONTACT_TYPES)
    label = models.CharField('Libellé', max_length=100, 
                             help_text='Ex: Service client, Commandes, Support technique...')
    value = models.CharField('Valeur', max_length=200,
                            help_text='Ex: contact@example.com, +33 1 23 45 67 89')
    is_primary = models.BooleanField('Principal', default=False,
                                     help_text='Affiché en priorité')
    is_active = models.BooleanField('Actif', default=True)
    show_in_header = models.BooleanField('Afficher dans le header', default=False)
    show_in_footer = models.BooleanField('Afficher dans le footer', default=True)
    order = models.PositiveIntegerField('Ordre d\'affichage', default=0)

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        ordering = ['order', '-is_primary', 'contact_type']

    def __str__(self):
        return f"{self.get_contact_type_display()} - {self.label}: {self.value}"


class Address(models.Model):
    """
    Adresses - Multiples entrées possibles
    """
    ADDRESS_TYPES = [
        ('main', '🏢 Siège social'),
        ('store', '🏪 Boutique'),
        ('warehouse', '📦 Entrepôt'),
        ('billing', '💳 Facturation'),
        ('other', '📍 Autre'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    address_type = models.CharField('Type', max_length=20, choices=ADDRESS_TYPES)
    label = models.CharField('Libellé', max_length=100, 
                             help_text='Ex: Siège Paris, Boutique Lyon...')
    street_line1 = models.CharField('Adresse ligne 1', max_length=255)
    street_line2 = models.CharField('Adresse ligne 2', max_length=255, blank=True)
    city = models.CharField('Ville', max_length=100)
    postal_code = models.CharField('Code postal', max_length=20)
    state = models.CharField('Région/État', max_length=100, blank=True)
    country = models.CharField('Pays', max_length=100, default='France')
    latitude = models.DecimalField('Latitude', max_digits=10, decimal_places=7, 
                                   null=True, blank=True)
    longitude = models.DecimalField('Longitude', max_digits=10, decimal_places=7, 
                                    null=True, blank=True)
    is_primary = models.BooleanField('Adresse principale', default=False)
    is_active = models.BooleanField('Active', default=True)
    show_in_footer = models.BooleanField('Afficher dans le footer', default=True)
    order = models.PositiveIntegerField('Ordre d\'affichage', default=0)

    class Meta:
        verbose_name = 'Adresse'
        verbose_name_plural = 'Adresses'
        ordering = ['order', '-is_primary']

    def __str__(self):
        return f"{self.label} - {self.city}"

    @property
    def full_address(self):
        parts = [self.street_line1]
        if self.street_line2:
            parts.append(self.street_line2)
        parts.append(f"{self.postal_code} {self.city}")
        if self.state:
            parts.append(self.state)
        parts.append(self.country)
        return ', '.join(parts)


class EmailSettings(models.Model):
    """
    Configuration email SMTP - Singleton
    """
    PROVIDERS = [
        ('gmail', 'Gmail'),
        ('outlook', 'Outlook/Hotmail'),
        ('yahoo', 'Yahoo'),
        ('custom', 'Serveur personnalisé'),
    ]

    provider = models.CharField('Fournisseur', max_length=20, choices=PROVIDERS, default='gmail')
    
    # SMTP Settings
    smtp_host = models.CharField('Serveur SMTP', max_length=200, default='smtp.gmail.com')
    smtp_port = models.PositiveIntegerField('Port SMTP', default=587)
    smtp_use_tls = models.BooleanField('Utiliser TLS', default=True)
    smtp_use_ssl = models.BooleanField('Utiliser SSL', default=False)
    smtp_username = models.CharField('Nom d\'utilisateur', max_length=200, blank=True,
                                     help_text='Votre adresse email complète')
    smtp_password = models.CharField('Mot de passe', max_length=200, blank=True,
                                     help_text='Pour Gmail: utilisez un mot de passe d\'application')
    
    # Emails par défaut
    default_from_email = models.EmailField('Email expéditeur', blank=True,
                                           help_text='Ex: noreply@votresite.com')
    default_from_name = models.CharField('Nom expéditeur', max_length=100, blank=True,
                                         help_text='Ex: Smile Shop')
    reply_to_email = models.EmailField('Email de réponse', blank=True)
    
    # Notifications admin
    admin_email = models.EmailField('Email admin (notifications)', blank=True,
                                    help_text='Recevra les notifications de commandes')
    send_order_notifications = models.BooleanField('Notifier nouvelles commandes', default=True)
    send_review_notifications = models.BooleanField('Notifier nouveaux avis', default=True)
    send_contact_notifications = models.BooleanField('Notifier messages contact', default=True)
    
    # Emails clients
    send_order_confirmation = models.BooleanField('Email confirmation commande', default=True)
    send_shipping_notification = models.BooleanField('Email expédition', default=True)
    send_invoice_email = models.BooleanField('Email facture', default=True)
    
    # Test
    is_configured = models.BooleanField('Configuration testée', default=False)
    last_test_date = models.DateTimeField('Dernier test', null=True, blank=True)
    last_test_result = models.TextField('Résultat du test', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuration Email'
        verbose_name_plural = 'Configuration Email'

    def __str__(self):
        return f"Config Email - {self.provider}"

    def save(self, *args, **kwargs):
        self.pk = 1
        # Pré-remplir selon le provider
        if self.provider == 'gmail' and not self.smtp_host:
            self.smtp_host = 'smtp.gmail.com'
            self.smtp_port = 587
            self.smtp_use_tls = True
        elif self.provider == 'outlook' and not self.smtp_host:
            self.smtp_host = 'smtp.office365.com'
            self.smtp_port = 587
            self.smtp_use_tls = True
        elif self.provider == 'yahoo' and not self.smtp_host:
            self.smtp_host = 'smtp.mail.yahoo.com'
            self.smtp_port = 587
            self.smtp_use_tls = True
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class PaymentSettings(models.Model):
    """
    Configuration des paiements - Singleton
    """
    # ============================================
    # PAIEMENT MOBILE HAITI
    # ============================================
    # MonCash (Digicel)
    moncash_enabled = models.BooleanField('MonCash activé', default=True)
    moncash_number = models.CharField('Numéro MonCash', max_length=20, blank=True,
                                      help_text='Ex: 37773508 (sans code pays)')
    moncash_name = models.CharField('Nom sur MonCash', max_length=100, blank=True,
                                    help_text='Nom affiché lors du transfert')
    
    # NatCash (Natcom)
    natcash_enabled = models.BooleanField('NatCash activé', default=True)
    natcash_number = models.CharField('Numéro NatCash', max_length=20, blank=True,
                                      help_text='Ex: 37773508 (sans code pays)')
    natcash_name = models.CharField('Nom sur NatCash', max_length=100, blank=True,
                                    help_text='Nom affiché lors du transfert')
    
    # Paiement à la livraison
    cod_enabled = models.BooleanField('Paiement à la livraison', default=True)
    cod_fee = models.DecimalField('Frais paiement à la livraison', max_digits=10, decimal_places=2, default=0)
    
    # ============================================
    # PAIEMENT INTERNATIONAL (optionnel)
    # ============================================
    # PayPal
    paypal_enabled = models.BooleanField('PayPal activé', default=False)
    paypal_mode = models.CharField('Mode PayPal', max_length=10, 
                                   choices=[('sandbox', 'Test (Sandbox)'), ('live', 'Production')],
                                   default='sandbox')
    paypal_client_id = models.CharField('PayPal Client ID', max_length=200, blank=True)
    paypal_client_secret = models.CharField('PayPal Secret', max_length=200, blank=True)
    paypal_webhook_id = models.CharField('PayPal Webhook ID', max_length=100, blank=True)
    
    # Stripe (pour plus tard)
    stripe_enabled = models.BooleanField('Stripe activé', default=False)
    stripe_mode = models.CharField('Mode Stripe', max_length=10,
                                   choices=[('test', 'Test'), ('live', 'Production')],
                                   default='test')
    stripe_public_key = models.CharField('Stripe Public Key', max_length=200, blank=True)
    stripe_secret_key = models.CharField('Stripe Secret Key', max_length=200, blank=True)
    stripe_webhook_secret = models.CharField('Stripe Webhook Secret', max_length=200, blank=True)
    
    # Virement bancaire
    bank_transfer_enabled = models.BooleanField('Virement bancaire activé', default=False)
    bank_name = models.CharField('Nom de la banque', max_length=100, blank=True)
    bank_iban = models.CharField('IBAN', max_length=50, blank=True)
    bank_bic = models.CharField('BIC/SWIFT', max_length=20, blank=True)
    bank_account_holder = models.CharField('Titulaire du compte', max_length=200, blank=True)
    
    # Options générales
    currency = models.CharField('Devise', max_length=3, default='HTG')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuration Paiement'
        verbose_name_plural = 'Configuration Paiement'

    def __str__(self):
        methods = []
        if self.paypal_enabled:
            methods.append('PayPal')
        if self.stripe_enabled:
            methods.append('Stripe')
        if self.bank_transfer_enabled:
            methods.append('Virement')
        if self.cod_enabled:
            methods.append('À la livraison')
        return f"Paiements: {', '.join(methods) or 'Aucun configuré'}"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(pk=1)
        return settings

    @property
    def available_methods(self):
        """Retourne les méthodes de paiement actives"""
        methods = []
        # Paiement à la livraison en premier (le plus utilisé en Haïti)
        if self.cod_enabled:
            methods.append({'id': 'cod', 'name': 'Paiement à la livraison', 'icon': 'bi-cash-stack'})
        # MonCash
        if self.moncash_enabled and self.moncash_number:
            methods.append({'id': 'moncash', 'name': 'MonCash', 'icon': 'bi-phone'})
        # NatCash
        if self.natcash_enabled and self.natcash_number:
            methods.append({'id': 'natcash', 'name': 'NatCash', 'icon': 'bi-phone'})
        # PayPal
        if self.paypal_enabled:
            methods.append({'id': 'paypal', 'name': 'PayPal', 'icon': 'bi-paypal'})
        # Stripe
        if self.stripe_enabled:
            methods.append({'id': 'stripe', 'name': 'Carte bancaire', 'icon': 'bi-credit-card'})
        # Virement bancaire
        if self.bank_transfer_enabled:
            methods.append({'id': 'bank', 'name': 'Virement bancaire', 'icon': 'bi-bank'})
        return methods


class ShippingMethod(models.Model):
    """
    Méthodes de livraison - Multiples entrées
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Nom', max_length=100)
    description = models.TextField('Description', blank=True)
    price = models.DecimalField('Prix', max_digits=10, decimal_places=2, default=0)
    free_from = models.DecimalField('Gratuit à partir de', max_digits=10, decimal_places=2, 
                                    null=True, blank=True)
    delivery_days_min = models.PositiveIntegerField('Délai min (jours)', default=1)
    delivery_days_max = models.PositiveIntegerField('Délai max (jours)', default=3)
    is_active = models.BooleanField('Actif', default=True)
    order = models.PositiveIntegerField('Ordre', default=0)

    class Meta:
        verbose_name = 'Méthode de livraison'
        verbose_name_plural = 'Méthodes de livraison'
        ordering = ['order', 'price']

    def __str__(self):
        return f"{self.name} - {self.price}€"

    @property
    def delivery_estimate(self):
        if self.delivery_days_min == self.delivery_days_max:
            return f"{self.delivery_days_min} jour(s)"
        return f"{self.delivery_days_min}-{self.delivery_days_max} jours"


class DeliveryZone(models.Model):
    """
    Zones de livraison en Haïti - Gérables depuis l'admin
    Permet d'activer/désactiver les zones où on livre
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Nom de la zone', max_length=100,
                            help_text='Ex: Port-au-Prince, Cap-Haïtien')
    areas = models.TextField('Zones/Quartiers couverts', blank=True,
                             help_text='Ex: Pétion-Ville, Delmas, Tabarre')
    delivery_time_min = models.PositiveIntegerField('Délai min (jours)', default=1)
    delivery_time_max = models.PositiveIntegerField('Délai max (jours)', default=2)
    delivery_cost = models.DecimalField('Coût de livraison', max_digits=10, decimal_places=2, 
                                        default=0, blank=True,
                                        help_text='0 = Contactez-nous pour le prix')
    cost_note = models.CharField('Note sur le prix', max_length=200, blank=True,
                                 help_text='Ex: "À partir de 500 HTG" ou "Contactez-nous"')
    is_active = models.BooleanField('Zone active', default=True,
                                    help_text='Décocher pour désactiver la livraison dans cette zone')
    order = models.PositiveIntegerField('Ordre d\'affichage', default=0)
    notes = models.TextField('Notes internes', blank=True,
                             help_text='Notes visibles uniquement dans l\'admin')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Zone de livraison'
        verbose_name_plural = 'Zones de livraison'
        ordering = ['order', 'name']

    def __str__(self):
        status = "✓" if self.is_active else "✗"
        return f"{status} {self.name}"

    @property
    def delivery_estimate(self):
        """Retourne l'estimation de délai"""
        if self.delivery_time_min == self.delivery_time_max:
            return f"{self.delivery_time_min} jour(s)"
        return f"{self.delivery_time_min}-{self.delivery_time_max} jours"

    @property
    def cost_display(self):
        """Retourne le coût formaté ou la note"""
        if self.cost_note:
            return self.cost_note
        if self.delivery_cost == 0:
            return "Contactez-nous"
        return f"{self.delivery_cost} HTG"

    @classmethod
    def get_active_zones(cls):
        """Retourne les zones actives (avec cache)"""
        zones = cache.get('active_delivery_zones')
        if zones is None:
            zones = list(cls.objects.filter(is_active=True).order_by('order', 'name'))
            cache.set('active_delivery_zones', zones, 3600)  # Cache 1h
        return zones

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Invalider le cache
        cache.delete('active_delivery_zones')

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        # Invalider le cache
        cache.delete('active_delivery_zones')


class CustomField(models.Model):
    """
    Champs personnalisés - Pour ajouter n'importe quelle info
    """
    FIELD_LOCATIONS = [
        ('header', 'Header'),
        ('footer', 'Footer'),
        ('contact', 'Page Contact'),
        ('about', 'Page À propos'),
        ('checkout', 'Page Commande'),
        ('product', 'Fiche produit'),
        ('other', 'Autre'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Nom du champ', max_length=100,
                            help_text='Nom interne (ex: horaires_samedi)')
    label = models.CharField('Libellé affiché', max_length=200,
                             help_text='Texte affiché (ex: Horaires du samedi)')
    value = models.TextField('Valeur',
                             help_text='Contenu du champ')
    icon = models.CharField('Icône Bootstrap', max_length=50, blank=True,
                            help_text='Ex: bi-clock, bi-geo-alt, bi-envelope')
    location = models.CharField('Emplacement', max_length=20, choices=FIELD_LOCATIONS)
    is_active = models.BooleanField('Actif', default=True)
    order = models.PositiveIntegerField('Ordre', default=0)

    class Meta:
        verbose_name = 'Champ personnalisé'
        verbose_name_plural = 'Champs personnalisés'
        ordering = ['location', 'order']

    def __str__(self):
        return f"{self.label} ({self.get_location_display()})"


class Banner(models.Model):
    """
    Bannières et annonces
    """
    BANNER_TYPES = [
        ('hero', 'Hero (Accueil)'),
        ('promo', 'Promotion'),
        ('announcement', 'Annonce (barre)'),
        ('popup', 'Popup'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('Titre', max_length=200)
    subtitle = models.CharField('Sous-titre', max_length=500, blank=True)
    image = models.ImageField('Image', upload_to='banners/', blank=True, null=True)
    background_color = models.CharField('Couleur de fond', max_length=20, blank=True,
                                        help_text='Ex: #FF5733 ou gradient')
    text_color = models.CharField('Couleur du texte', max_length=20, default='#FFFFFF')
    button_text = models.CharField('Texte du bouton', max_length=50, blank=True)
    button_url = models.CharField('Lien du bouton', max_length=500, blank=True)
    banner_type = models.CharField('Type', max_length=20, choices=BANNER_TYPES)
    is_active = models.BooleanField('Active', default=True)
    start_date = models.DateTimeField('Date de début', null=True, blank=True)
    end_date = models.DateTimeField('Date de fin', null=True, blank=True)
    order = models.PositiveIntegerField('Ordre', default=0)

    class Meta:
        verbose_name = 'Bannière'
        verbose_name_plural = 'Bannières'
        ordering = ['order', '-start_date']

    def __str__(self):
        return f"{self.get_banner_type_display()} - {self.title}"


class LegalPage(models.Model):
    """
    Pages légales - CGV, Mentions légales, Politique de confidentialité, etc.
    """
    PAGE_TYPES = [
        ('cgv', 'CGV'),
        ('legal', 'Mentions légales'),
        ('privacy', 'Politique de confidentialité'),
        ('cookies', 'Politique des cookies'),
        ('returns', 'Politique de retour'),
        ('shipping', 'Politique de livraison'),
        ('about', 'À propos'),
        ('faq', 'FAQ'),
        ('custom', 'Page personnalisée'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page_type = models.CharField('Type de page', max_length=20, choices=PAGE_TYPES)
    title = models.CharField('Titre', max_length=200)
    slug = models.SlugField('URL', unique=True)
    content = models.TextField('Contenu', help_text='Supporte le HTML')
    meta_title = models.CharField('Titre SEO', max_length=200, blank=True)
    meta_description = models.TextField('Description SEO', blank=True)
    is_active = models.BooleanField('Active', default=True)
    show_in_footer = models.BooleanField('Afficher dans le footer', default=True)
    order = models.PositiveIntegerField('Ordre', default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Page légale'
        verbose_name_plural = 'Pages légales'
        ordering = ['order']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('core:legal_page', kwargs={'slug': self.slug})


class Currency(models.Model):
    """
    Devises disponibles sur le site avec taux de conversion
    """
    CURRENCY_CHOICES = [
        ('EUR', 'Euro (€)'),
        ('USD', 'US Dollar ($)'),
        ('CAD', 'Canadian Dollar (CA$)'),
        ('GBP', 'British Pound (£)'),
        ('HTG', 'Haitian Gourde (G)'),
    ]
    
    code = models.CharField('Code devise', max_length=3, choices=CURRENCY_CHOICES, unique=True)
    name = models.CharField('Nom', max_length=50)
    symbol = models.CharField('Symbole', max_length=10)
    exchange_rate = models.DecimalField(
        'Taux de change',
        max_digits=12,
        decimal_places=6,
        default=1.0,
        help_text='Taux par rapport à la devise de base (EUR). Ex: 1 EUR = X cette devise'
    )
    is_default = models.BooleanField('Devise par défaut', default=False)
    is_active = models.BooleanField('Actif', default=True)
    position = models.CharField(
        'Position du symbole',
        max_length=10,
        choices=[('before', 'Avant le montant'), ('after', 'Après le montant')],
        default='after'
    )
    decimal_places = models.PositiveSmallIntegerField('Décimales', default=2)
    thousands_separator = models.CharField('Séparateur milliers', max_length=1, default=' ')
    decimal_separator = models.CharField('Séparateur décimal', max_length=1, default=',')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Devise'
        verbose_name_plural = 'Devises'
        ordering = ['-is_default', 'name']

    def __str__(self):
        return f"{self.name} ({self.symbol})"

    def save(self, *args, **kwargs):
        # Si c'est la devise par défaut, désactiver les autres
        if self.is_default:
            Currency.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
        # Invalider le cache
        cache.delete('currencies')
        cache.delete('default_currency')

    @classmethod
    def get_default(cls):
        """Récupère la devise par défaut"""
        currency = cache.get('default_currency')
        if not currency:
            currency = cls.objects.filter(is_default=True, is_active=True).first()
            if not currency:
                currency = cls.objects.filter(is_active=True).first()
            if currency:
                cache.set('default_currency', currency, 3600)
        return currency

    @classmethod
    def get_active_currencies(cls):
        """Récupère toutes les devises actives"""
        currencies = cache.get('currencies')
        if not currencies:
            currencies = list(cls.objects.filter(is_active=True))
            cache.set('currencies', currencies, 3600)
        return currencies

    def convert_from_base(self, amount):
        """Convertit un montant de la devise de base vers cette devise"""
        from decimal import Decimal
        return Decimal(str(amount)) * self.exchange_rate

    def convert_to_base(self, amount):
        """Convertit un montant de cette devise vers la devise de base"""
        from decimal import Decimal
        if self.exchange_rate == 0:
            return Decimal('0')
        return Decimal(str(amount)) / self.exchange_rate

    def format_price(self, amount):
        """Formate un prix dans cette devise"""
        from decimal import Decimal, ROUND_HALF_UP
        
        # Convertir le montant
        converted = self.convert_from_base(amount)
        
        # Arrondir
        rounded = converted.quantize(
            Decimal(10) ** -self.decimal_places,
            rounding=ROUND_HALF_UP
        )
        
        # Formater avec séparateurs
        parts = str(rounded).split('.')
        integer_part = parts[0]
        decimal_part = parts[1] if len(parts) > 1 else '00'
        
        # Ajouter séparateur de milliers
        if self.thousands_separator:
            integer_part = self._add_thousands_sep(integer_part)
        
        # Construire le nombre formaté
        formatted_number = f"{integer_part}{self.decimal_separator}{decimal_part[:self.decimal_places].ljust(self.decimal_places, '0')}"
        
        # Ajouter le symbole
        if self.position == 'before':
            return f"{self.symbol}{formatted_number}"
        else:
            return f"{formatted_number} {self.symbol}"

    def _add_thousands_sep(self, s):
        """Ajoute le séparateur de milliers"""
        if len(s) <= 3:
            return s
        return self._add_thousands_sep(s[:-3]) + self.thousands_separator + s[-3:]


class Language(models.Model):
    """
    Langues disponibles sur le site.
    Permet d'activer/désactiver les langues depuis l'admin.
    """
    LANGUAGE_CHOICES = [
        ('fr', 'Français'),
        ('en', 'English'),
        ('ht', 'Kreyòl Ayisyen'),
        ('es', 'Español'),
        ('pt', 'Português'),
        ('de', 'Deutsch'),
        ('it', 'Italiano'),
    ]
    
    code = models.CharField(
        'Code langue',
        max_length=5,
        choices=LANGUAGE_CHOICES,
        unique=True
    )
    name = models.CharField('Nom', max_length=50)
    native_name = models.CharField('Nom natif', max_length=50, help_text='Ex: Français, English')
    flag_emoji = models.CharField('Emoji drapeau', max_length=10, default='🌐', help_text='Ex: 🇫🇷, 🇬🇧')
    is_default = models.BooleanField('Langue par défaut', default=False)
    is_active = models.BooleanField('Active', default=True)
    order = models.PositiveIntegerField('Ordre', default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Langue'
        verbose_name_plural = 'Langues'
        ordering = ['order', '-is_default', 'name']

    def __str__(self):
        return f"{self.flag_emoji} {self.native_name}"

    def save(self, *args, **kwargs):
        # Une seule langue par défaut
        if self.is_default:
            Language.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
        # Invalider le cache
        cache.delete('languages')
        cache.delete('default_language')

    @classmethod
    def get_default(cls):
        """Récupère la langue par défaut"""
        lang = cache.get('default_language')
        if not lang:
            lang = cls.objects.filter(is_default=True, is_active=True).first()
            if not lang:
                lang = cls.objects.filter(is_active=True).first()
            if lang:
                cache.set('default_language', lang, 3600)
        return lang

    @classmethod
    def get_active_languages(cls):
        """Récupère toutes les langues actives"""
        languages = cache.get('languages')
        if not languages:
            languages = list(cls.objects.filter(is_active=True))
            cache.set('languages', languages, 3600)
        return languages

