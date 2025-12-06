from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import Category, Product, ProductImage, StockMovement, Cart, CartItem, Coupon


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'product_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'name', 'category', 'price_display', 'stock_status', 
                    'is_active', 'is_featured', 'created_at']
    list_filter = ['is_active', 'is_featured', 'category', 'created_at']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'is_featured']
    readonly_fields = ['created_at', 'updated_at', 'profit_margin_display']
    inlines = [ProductImageInline]  # ProductVariantInline ajouté après définition
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'slug', 'short_description', 'description', 'category', 'image')
        }),
        ('Prix', {
            'fields': ('price', 'compare_at_price', 'cost_price', 'profit_margin_display')
        }),
        ('Stock', {
            'fields': ('stock_quantity', 'low_stock_threshold', 'track_stock', 'sku', 'barcode')
        }),
        ('Options', {
            'fields': ('is_active', 'is_featured', 'weight')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return '📷'
    image_preview.short_description = 'Image'

    def price_display(self, obj):
        if obj.is_on_sale:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">{} €</span> '
                '<strong style="color: #e74c3c;">{} €</strong>',
                obj.compare_at_price, obj.price
            )
        return f'{obj.price} €'
    price_display.short_description = 'Prix'

    def stock_status(self, obj):
        if not obj.track_stock:
            return format_html('<span style="color: #666;">Non suivi</span>')
        if obj.stock_quantity == 0:
            return format_html('<span style="color: #e74c3c; font-weight: bold;">🔴 Rupture</span>')
        if obj.is_low_stock:
            return format_html('<span style="color: #f39c12; font-weight: bold;">🟡 {} (bas)</span>', obj.stock_quantity)
        return format_html('<span style="color: #27ae60;">🟢 {}</span>', obj.stock_quantity)
    stock_status.short_description = 'Stock'

    def profit_margin_display(self, obj):
        margin = obj.profit_margin
        if margin:
            return f'{margin:.1f}%'
        return '-'
    profit_margin_display.short_description = 'Marge'


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'product', 'movement_type', 'quantity', 'reason', 'created_by']
    list_filter = ['movement_type', 'created_at', 'product']
    search_fields = ['product__name', 'reason', 'notes']
    readonly_fields = ['created_at']
    autocomplete_fields = ['product']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_display', 'minimum_amount', 'usage_display', 'is_active', 'expires_at']
    list_filter = ['is_active', 'discount_type', 'expires_at']
    search_fields = ['code', 'description']
    list_editable = ['is_active']

    def discount_display(self, obj):
        if obj.discount_type == 'percentage':
            return f'{obj.discount_value}%'
        return f'{obj.discount_value} €'
    discount_display.short_description = 'Réduction'

    def usage_display(self, obj):
        if obj.max_uses:
            return f'{obj.used_count}/{obj.max_uses}'
        return f'{obj.used_count}'
    usage_display.short_description = 'Utilisations'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_items', 'subtotal', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'session_key']


# ==============================================
# AVIS PRODUITS
# ==============================================

from .models import ProductReview, Wishlist, VariantAttribute, VariantAttributeValue, ProductVariant


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating_display', 'title', 'is_approved', 'is_verified_purchase', 'helpful_votes', 'created_at']
    list_filter = ['is_approved', 'is_verified_purchase', 'rating', 'created_at']
    search_fields = ['product__name', 'user__email', 'title', 'comment']
    list_editable = ['is_approved']
    readonly_fields = ['created_at', 'updated_at', 'helpful_votes']
    actions = ['approve_reviews', 'reject_reviews']
    
    fieldsets = (
        ('Informations', {
            'fields': ('product', 'user', 'rating', 'title', 'comment')
        }),
        ('Statut', {
            'fields': ('is_approved', 'is_verified_purchase', 'helpful_votes')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def rating_display(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #f59e0b;">{}</span>', stars)
    rating_display.short_description = 'Note'

    @admin.action(description="✅ Approuver les avis sélectionnés")
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} avis approuvé(s).')

    @admin.action(description="❌ Rejeter les avis sélectionnés")
    def reject_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} avis rejeté(s).')


# ==============================================
# WISHLIST
# ==============================================

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product_count', 'updated_at']
    search_fields = ['user__email', 'user__username']
    filter_horizontal = ['products']

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Produits'


# ==============================================
# VARIANTES PRODUITS
# ==============================================

@admin.register(VariantAttribute)
class VariantAttributeAdmin(admin.ModelAdmin):
    list_display = ['name', 'values_count']
    search_fields = ['name']

    def values_count(self, obj):
        return obj.values.count()
    values_count.short_description = 'Valeurs'


@admin.register(VariantAttributeValue)
class VariantAttributeValueAdmin(admin.ModelAdmin):
    list_display = ['attribute', 'value', 'color_display']
    list_filter = ['attribute']
    search_fields = ['value']

    def color_display(self, obj):
        if obj.color_code:
            return format_html(
                '<span style="display:inline-block;width:20px;height:20px;background:{};border:1px solid #ccc;border-radius:3px;"></span> {}',
                obj.color_code, obj.color_code
            )
        return '-'
    color_display.short_description = 'Couleur'


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['name', 'sku', 'price_adjustment', 'stock_quantity', 'is_active']

# Ajouter les variantes à l'admin produit
ProductAdmin.inlines = [ProductImageInline, ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'sku', 'price_adjustment', 'stock_quantity', 'final_price_display', 'is_active']
    list_filter = ['is_active', 'product__category']
    search_fields = ['product__name', 'sku', 'name']
    list_editable = ['is_active', 'stock_quantity', 'price_adjustment']
    filter_horizontal = ['attributes']

    def final_price_display(self, obj):
        return f'{obj.final_price} €'
    final_price_display.short_description = 'Prix final'

