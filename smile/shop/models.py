from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
import uuid


class Category(models.Model):
    """Catégorie de produits"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Nom', max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField('Description', blank=True)
    image = models.ImageField('Image', upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='children', verbose_name='Catégorie parente')
    is_active = models.BooleanField('Active', default=True)
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField('Modifié le', auto_now=True)

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:category', kwargs={'slug': self.slug})

    @property
    def product_count(self):
        return self.products.filter(is_active=True).count()


class Product(models.Model):
    """Produit"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Nom', max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField('Description', blank=True)
    short_description = models.CharField('Description courte', max_length=500, blank=True)
    
    # Prix
    price = models.DecimalField('Prix', max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField('Prix barré', max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField('Prix d\'achat', max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Identification
    sku = models.CharField('SKU', max_length=100, unique=True, blank=True, null=True)
    barcode = models.CharField('Code-barres', max_length=100, blank=True)
    
    # Catégorie et images
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='products', verbose_name='Catégorie')
    image = models.ImageField('Image principale', upload_to='products/', blank=True, null=True)
    
    # Stock
    stock_quantity = models.PositiveIntegerField('Quantité en stock', default=0)
    low_stock_threshold = models.PositiveIntegerField('Seuil stock bas', default=10)
    track_stock = models.BooleanField('Suivre le stock', default=True)
    
    # Caractéristiques
    weight = models.DecimalField('Poids (kg)', max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Statut
    is_active = models.BooleanField('Actif', default=True)
    is_featured = models.BooleanField('Mis en avant', default=False)
    
    # SEO
    meta_title = models.CharField('Titre SEO', max_length=255, blank=True)
    meta_description = models.TextField('Description SEO', blank=True)
    
    # Dates
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField('Modifié le', auto_now=True)

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            # Génère un SKU automatique avec les paramètres du site
            try:
                from core.models import SiteSettings
                settings = SiteSettings.get_settings()
                self.sku = settings.get_next_sku()
            except:
                self.sku = f"SKU-{str(self.id)[:8].upper()}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:product_detail', kwargs={'slug': self.slug})

    @property
    def is_on_sale(self):
        return self.compare_at_price and self.compare_at_price > self.price

    @property
    def discount_percentage(self):
        if self.is_on_sale:
            return int(((self.compare_at_price - self.price) / self.compare_at_price) * 100)
        return 0

    @property
    def is_in_stock(self):
        if not self.track_stock:
            return True
        return self.stock_quantity > 0

    @property
    def is_low_stock(self):
        return self.track_stock and self.stock_quantity <= self.low_stock_threshold

    @property
    def profit_margin(self):
        if self.cost_price and self.cost_price > 0:
            return ((self.price - self.cost_price) / self.price) * 100
        return None

    # Propriétés pour les avis
    @property
    def average_rating(self):
        """Note moyenne des avis approuvés"""
        from django.db.models import Avg
        avg = self.reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0

    @property
    def review_count(self):
        """Nombre d'avis approuvés"""
        return self.reviews.filter(is_approved=True).count()

    @property
    def rating_distribution(self):
        """Distribution des notes (pour affichage)"""
        distribution = {}
        total = self.review_count
        for i in range(1, 6):
            count = self.reviews.filter(is_approved=True, rating=i).count()
            distribution[i] = {
                'count': count,
                'percentage': int((count / total * 100) if total > 0 else 0)
            }
        return distribution

    # Propriétés pour les variantes
    @property
    def has_variants(self):
        """Vérifie si le produit a des variantes actives"""
        return self.variants.filter(is_active=True).exists()

    @property
    def available_attributes(self):
        """Retourne les attributs disponibles pour ce produit"""
        attributes = {}
        for variant in self.variants.filter(is_active=True):
            for attr_value in variant.attributes.all():
                attr_name = attr_value.attribute.name
                if attr_name not in attributes:
                    attributes[attr_name] = []
                if attr_value not in attributes[attr_name]:
                    attributes[attr_name].append(attr_value)
        return attributes


class ProductImage(models.Model):
    """Images supplémentaires du produit"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField('Image', upload_to='products/')
    alt_text = models.CharField('Texte alternatif', max_length=255, blank=True)
    position = models.PositiveIntegerField('Position', default=0)

    class Meta:
        verbose_name = 'Image produit'
        verbose_name_plural = 'Images produit'
        ordering = ['position']


class StockMovement(models.Model):
    """Mouvement de stock"""
    MOVEMENT_TYPES = [
        ('in', '➕ Entrée'),
        ('out', '➖ Sortie'),
        ('adjustment', '🔄 Ajustement'),
        ('return', '↩️ Retour'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements',
                                verbose_name='Produit')
    movement_type = models.CharField('Type', max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField('Quantité')
    reason = models.CharField('Raison', max_length=255, blank=True)
    notes = models.TextField('Notes', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Par')
    created_at = models.DateTimeField('Date', auto_now_add=True)

    class Meta:
        verbose_name = 'Mouvement de stock'
        verbose_name_plural = 'Mouvements de stock'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity})"

    def save(self, *args, **kwargs):
        # Mettre à jour le stock du produit
        if not self.pk:  # Nouveau mouvement
            if self.movement_type in ['in', 'return']:
                self.product.stock_quantity += abs(self.quantity)
            elif self.movement_type == 'out':
                self.product.stock_quantity -= abs(self.quantity)
            elif self.movement_type == 'adjustment':
                self.product.stock_quantity = self.quantity
            self.product.save()
        super().save(*args, **kwargs)


class Cart(models.Model):
    """Panier"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField('Session', max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Panier'
        verbose_name_plural = 'Paniers'

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """Article du panier"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField('Quantité', default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'product']

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Coupon(models.Model):
    """Coupon de réduction"""
    DISCOUNT_TYPES = [
        ('percentage', 'Pourcentage'),
        ('fixed', 'Montant fixe'),
    ]

    code = models.CharField('Code', max_length=50, unique=True)
    description = models.TextField('Description', blank=True)
    discount_type = models.CharField('Type', max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField('Valeur', max_digits=10, decimal_places=2)
    minimum_amount = models.DecimalField('Montant minimum', max_digits=10, decimal_places=2, default=0)
    max_uses = models.PositiveIntegerField('Utilisations max', null=True, blank=True)
    used_count = models.PositiveIntegerField('Utilisations', default=0)
    starts_at = models.DateTimeField('Début', null=True, blank=True)
    expires_at = models.DateTimeField('Expiration', null=True, blank=True)
    is_active = models.BooleanField('Actif', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'

    def __str__(self):
        return self.code


# ==============================================
# AVIS ET NOTES PRODUITS
# ==============================================

class ProductReview(models.Model):
    """Avis sur un produit"""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews',
                                verbose_name='Produit')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews',
                             verbose_name='Utilisateur')
    rating = models.PositiveSmallIntegerField('Note', choices=RATING_CHOICES)
    title = models.CharField('Titre', max_length=100)
    comment = models.TextField('Commentaire')
    is_approved = models.BooleanField('Approuvé', default=False)
    is_verified_purchase = models.BooleanField('Achat vérifié', default=False)
    helpful_votes = models.PositiveIntegerField('Votes utiles', default=0)
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField('Modifié le', auto_now=True)

    class Meta:
        verbose_name = 'Avis produit'
        verbose_name_plural = 'Avis produits'
        ordering = ['-created_at']
        unique_together = ['product', 'user']  # Un seul avis par utilisateur par produit

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}★)"

    @property
    def stars_html(self):
        """Retourne les étoiles en HTML"""
        full = '★' * self.rating
        empty = '☆' * (5 - self.rating)
        return full + empty


# ==============================================
# WISHLIST / FAVORIS
# ==============================================

class Wishlist(models.Model):
    """Liste de souhaits"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist',
                                verbose_name='Utilisateur')
    products = models.ManyToManyField(Product, related_name='wishlisted_by', blank=True,
                                      verbose_name='Produits')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Liste de souhaits'
        verbose_name_plural = 'Listes de souhaits'

    def __str__(self):
        return f"Wishlist de {self.user.username}"

    @property
    def count(self):
        return self.products.count()


# ==============================================
# VARIANTES PRODUITS
# ==============================================

class VariantAttribute(models.Model):
    """Attributs de variantes (Taille, Couleur, etc.)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Nom', max_length=50)  # Ex: Taille, Couleur
    
    class Meta:
        verbose_name = 'Attribut de variante'
        verbose_name_plural = 'Attributs de variantes'
        ordering = ['name']

    def __str__(self):
        return self.name


class VariantAttributeValue(models.Model):
    """Valeurs d'attributs (S, M, L / Rouge, Bleu, etc.)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attribute = models.ForeignKey(VariantAttribute, on_delete=models.CASCADE, 
                                  related_name='values', verbose_name='Attribut')
    value = models.CharField('Valeur', max_length=100)  # Ex: S, M, L / Rouge, Bleu
    color_code = models.CharField('Code couleur', max_length=7, blank=True, 
                                  help_text='Code hexadécimal pour les couleurs (ex: #FF0000)')

    class Meta:
        verbose_name = 'Valeur d\'attribut'
        verbose_name_plural = 'Valeurs d\'attributs'
        ordering = ['attribute', 'value']
        unique_together = ['attribute', 'value']

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class ProductVariant(models.Model):
    """Variante d'un produit"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants',
                                verbose_name='Produit')
    sku = models.CharField('SKU Variante', max_length=100, unique=True, blank=True, null=True)
    name = models.CharField('Nom variante', max_length=255, blank=True, 
                            help_text='Ex: Rouge - XL')
    attributes = models.ManyToManyField(VariantAttributeValue, related_name='variants',
                                        verbose_name='Attributs')
    price_adjustment = models.DecimalField('Ajustement de prix', max_digits=10, decimal_places=2, 
                                           default=0, help_text='Montant à ajouter/soustraire du prix de base')
    stock_quantity = models.PositiveIntegerField('Stock', default=0)
    image = models.ImageField('Image variante', upload_to='products/variants/', blank=True, null=True)
    is_active = models.BooleanField('Actif', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Variante produit'
        verbose_name_plural = 'Variantes produits'

    def __str__(self):
        if self.name:
            return f"{self.product.name} - {self.name}"
        attrs = ", ".join([str(attr) for attr in self.attributes.all()])
        return f"{self.product.name} ({attrs})"

    @property
    def final_price(self):
        """Prix final avec ajustement"""
        return self.product.price + self.price_adjustment

    def save(self, *args, **kwargs):
        if not self.sku:
            # Générer un SKU automatique
            base_sku = self.product.sku or f"SKU-{str(self.product.id)[:8].upper()}"
            self.sku = f"{base_sku}-V{str(self.id)[:4].upper()}"
        super().save(*args, **kwargs)
