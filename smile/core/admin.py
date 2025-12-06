"""
Administration complète de la configuration du site
Tout est gérable depuis l'admin Django
"""
from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.template.response import TemplateResponse
from django.conf import settings
from .models import (
    SiteSettings, ContactInfo, Address, EmailSettings,
    PaymentSettings, ShippingMethod, CustomField, Banner, LegalPage, Currency, Language
)


# ============================================
# LANGUES - Activer/Désactiver les langues du site
# ============================================

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    """Admin pour les langues - activez/désactivez les langues disponibles"""
    list_display = ['flag_display', 'native_name', 'name', 'code', 'is_default', 'is_active', 'order']
    list_filter = ['is_active', 'is_default']
    list_editable = ['is_active', 'order']
    search_fields = ['name', 'native_name', 'code']
    ordering = ['order', '-is_default', 'name']
    
    fieldsets = (
        ('🌐 Langue', {
            'fields': ('code', 'name', 'native_name', 'flag_emoji'),
        }),
        ('⚙️ Paramètres', {
            'fields': ('is_default', 'is_active', 'order'),
            'description': 'Activez/désactivez les langues et définissez l\'ordre d\'affichage.',
        }),
    )
    
    def flag_display(self, obj):
        return f"{obj.flag_emoji} {obj.code.upper()}"
    flag_display.short_description = 'Langue'
    
    actions = ['activate_languages', 'deactivate_languages']
    
    @admin.action(description='✅ Activer les langues sélectionnées')
    def activate_languages(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} langue(s) activée(s).')
    
    @admin.action(description='❌ Désactiver les langues sélectionnées')
    def deactivate_languages(self, request, queryset):
        # Ne pas désactiver la langue par défaut
        count = queryset.filter(is_default=False).update(is_active=False)
        self.message_user(request, f'{count} langue(s) désactivée(s).')


# ============================================
# DEVISES - Activer/Désactiver et mettre à jour les taux
# ============================================

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    """Admin pour les devises - activez/désactivez et mettez à jour les taux"""
    list_display = ['symbol_display', 'name', 'code', 'exchange_rate_display', 'is_default', 'is_active', 'updated_at']
    list_filter = ['is_active', 'is_default']
    list_editable = ['is_active']
    search_fields = ['name', 'code']
    ordering = ['-is_default', 'name']
    readonly_fields = ['updated_at']
    
    fieldsets = (
        ('💱 Informations de base', {
            'fields': ('code', 'name', 'symbol', 'is_default', 'is_active'),
        }),
        ('💰 Taux de change', {
            'fields': ('exchange_rate',),
            'description': 'Taux par rapport à l\'Euro (EUR). Cliquez sur "Mettre à jour les taux" pour récupérer les taux du jour.',
        }),
        ('🔧 Format d\'affichage', {
            'fields': ('position', 'decimal_places', 'thousands_separator', 'decimal_separator'),
        }),
        ('📅 Informations', {
            'fields': ('updated_at',),
        }),
    )
    
    def symbol_display(self, obj):
        return f"{obj.symbol} {obj.code}"
    symbol_display.short_description = 'Devise'
    
    def exchange_rate_display(self, obj):
        if obj.code == 'EUR':
            return '1.00 (base)'
        return f"{obj.exchange_rate:.4f}"
    exchange_rate_display.short_description = 'Taux'
    
    actions = ['activate_currencies', 'deactivate_currencies', 'update_exchange_rates']
    
    @admin.action(description='✅ Activer les devises sélectionnées')
    def activate_currencies(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} devise(s) activée(s).')
    
    @admin.action(description='❌ Désactiver les devises sélectionnées')
    def deactivate_currencies(self, request, queryset):
        # Ne pas désactiver la devise par défaut
        count = queryset.filter(is_default=False).update(is_active=False)
        self.message_user(request, f'{count} devise(s) désactivée(s).')
    
    @admin.action(description='🔄 Mettre à jour les taux de change (API)')
    def update_exchange_rates(self, request, queryset):
        try:
            from core.services.currency_updater import CurrencyUpdater
            updater = CurrencyUpdater()
            updated = updater.update_database_rates()
            self.message_user(request, f'✅ {updated} taux de change mis à jour depuis la BCE.', messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f'❌ Erreur: {e}', messages.ERROR)
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = '💱 Gestion des Devises'
        return super().changelist_view(request, extra_context=extra_context)


# ============================================
# CONFIGURATION GÉNÉRALE DU SITE (Singleton)
# ============================================

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Admin pour la configuration générale du site"""
    
    fieldsets = (
        ('🏪 Informations générales', {
            'fields': ('site_name', 'site_slogan', 'site_description', 'logo', 'favicon'),
        }),
        ('🏢 Informations légales', {
            'fields': ('company_name', 'siret', 'tva_number', 'rcs', 'capital'),
            'classes': ('collapse',),
        }),
        ('📱 Réseaux sociaux', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url', 'youtube_url', 
                      'linkedin_url', 'tiktok_url', 'whatsapp_number'),
            'classes': ('collapse',),
        }),
        ('🔍 SEO & Analytics', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 
                      'google_analytics_id', 'facebook_pixel_id'),
            'classes': ('collapse',),
        }),
        ('💰 Paramètres boutique', {
            'fields': ('currency', 'currency_symbol', 'tax_rate', 
                      'shipping_cost', 'free_shipping_threshold'),
        }),
        ('🔢 Numérotation automatique', {
            'fields': ('order_prefix', 'order_next_number', 
                      'invoice_prefix', 'invoice_next_number',
                      'product_sku_prefix', 'product_next_number'),
            'description': 'Configure les préfixes et numéros pour les commandes, factures et produits',
        }),
        ('⚙️ Options', {
            'fields': ('maintenance_mode', 'maintenance_message', 'allow_guest_checkout',
                      'reviews_require_approval', 'show_stock_quantity', 'low_stock_threshold'),
        }),
        ('🕐 Horaires', {
            'fields': ('opening_hours',),
        }),
    )

    def has_add_permission(self, request):
        # Un seul objet SiteSettings autorisé
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # Redirige directement vers l'édition de l'objet unique
        obj, created = SiteSettings.objects.get_or_create(pk=1)
        return HttpResponseRedirect(
            reverse('admin:core_sitesettings_change', args=[obj.pk])
        )


# ============================================
# CONTACTS (illimités)
# ============================================

@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    """Admin pour les contacts - ajoutez autant que vous voulez!"""
    
    list_display = ('icon_display', 'label', 'value', 'contact_type', 
                    'is_primary', 'show_in_header', 'show_in_footer', 'is_active', 'order')
    list_display_links = ('label', 'value')
    list_editable = ('is_primary', 'show_in_header', 'show_in_footer', 'is_active', 'order')
    list_filter = ('contact_type', 'is_primary', 'is_active', 'show_in_header', 'show_in_footer')
    search_fields = ('label', 'value')
    ordering = ('order', '-is_primary')

    fieldsets = (
        ('📝 Informations', {
            'fields': ('contact_type', 'label', 'value'),
        }),
        ('🎯 Affichage', {
            'fields': ('is_primary', 'is_active', 'show_in_header', 'show_in_footer', 'order'),
        }),
    )

    def icon_display(self, obj):
        icons = {
            'email': '📧',
            'phone': '📞',
            'mobile': '📱',
            'fax': '📠',
            'whatsapp': '💬',
        }
        return icons.get(obj.contact_type, '📋')
    icon_display.short_description = ''


# ============================================
# ADRESSES (illimitées)
# ============================================

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin pour les adresses - autant que nécessaire!"""
    
    list_display = ('icon_display', 'label', 'city', 'country', 'address_type', 
                    'is_primary', 'show_in_footer', 'is_active', 'order')
    list_display_links = ('label', 'city')
    list_editable = ('is_primary', 'show_in_footer', 'is_active', 'order')
    list_filter = ('address_type', 'is_primary', 'is_active', 'country')
    search_fields = ('label', 'street_line1', 'city', 'postal_code')
    ordering = ('order', '-is_primary')

    fieldsets = (
        ('📍 Type et libellé', {
            'fields': ('address_type', 'label'),
        }),
        ('🏠 Adresse', {
            'fields': ('street_line1', 'street_line2', 'postal_code', 'city', 'state', 'country'),
        }),
        ('🗺️ Coordonnées GPS (optionnel)', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',),
        }),
        ('🎯 Affichage', {
            'fields': ('is_primary', 'is_active', 'show_in_footer', 'order'),
        }),
    )

    def icon_display(self, obj):
        icons = {
            'main': '🏢',
            'store': '🏪',
            'warehouse': '📦',
            'billing': '💳',
            'other': '📍',
        }
        return icons.get(obj.address_type, '📍')
    icon_display.short_description = ''


# ============================================
# CONFIGURATION EMAIL (Singleton)
# ============================================

@admin.register(EmailSettings)
class EmailSettingsAdmin(admin.ModelAdmin):
    """Configuration email avec test intégré"""
    
    change_form_template = 'admin/core/emailsettings/change_form.html'
    
    fieldsets = (
        ('📧 Fournisseur email', {
            'fields': ('provider',),
            'description': 'Pour Gmail: créez un mot de passe d\'application dans les paramètres de sécurité Google',
        }),
        ('🔧 Configuration SMTP', {
            'fields': ('smtp_host', 'smtp_port', 'smtp_use_tls', 'smtp_use_ssl', 
                      'smtp_username', 'smtp_password'),
        }),
        ('✉️ Emails par défaut', {
            'fields': ('default_from_email', 'default_from_name', 'reply_to_email'),
        }),
        ('🔔 Notifications admin', {
            'fields': ('admin_email', 'send_order_notifications', 
                      'send_review_notifications', 'send_contact_notifications'),
        }),
        ('📤 Emails clients', {
            'fields': ('send_order_confirmation', 'send_shipping_notification', 'send_invoice_email'),
        }),
        ('✅ Statut', {
            'fields': ('is_configured', 'last_test_date', 'last_test_result'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('is_configured', 'last_test_date', 'last_test_result')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('test-email/', self.admin_site.admin_view(self.test_email_view), 
                 name='core_emailsettings_test'),
        ]
        return custom_urls + urls

    def test_email_view(self, request):
        """Vue pour tester l'envoi d'email"""
        from datetime import datetime
        
        email_settings = EmailSettings.get_settings()
        test_email = request.POST.get('test_email', email_settings.admin_email)
        
        if request.method == 'POST' and test_email:
            try:
                # Configure dynamiquement les settings Django
                from django.core.mail import get_connection
                
                connection = get_connection(
                    host=email_settings.smtp_host,
                    port=email_settings.smtp_port,
                    username=email_settings.smtp_username,
                    password=email_settings.smtp_password,
                    use_tls=email_settings.smtp_use_tls,
                    use_ssl=email_settings.smtp_use_ssl,
                )
                
                email = EmailMessage(
                    subject='🧪 Test email - Smile Shop',
                    body=f'''
Bonjour!

Ceci est un email de test envoyé depuis l'administration de votre site Smile Shop.

Si vous recevez ce message, votre configuration email fonctionne correctement! ✅

Date du test: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
Serveur SMTP: {email_settings.smtp_host}:{email_settings.smtp_port}

Cordialement,
L'équipe Smile Shop
                    ''',
                    from_email=f"{email_settings.default_from_name} <{email_settings.default_from_email or email_settings.smtp_username}>",
                    to=[test_email],
                    connection=connection,
                )
                email.send()
                
                # Mise à jour du statut
                email_settings.is_configured = True
                email_settings.last_test_date = datetime.now()
                email_settings.last_test_result = f'✅ Succès - Email envoyé à {test_email}'
                email_settings.save()
                
                messages.success(request, f'✅ Email de test envoyé avec succès à {test_email}!')
                
            except Exception as e:
                email_settings.is_configured = False
                email_settings.last_test_date = datetime.now()
                email_settings.last_test_result = f'❌ Erreur: {str(e)}'
                email_settings.save()
                
                messages.error(request, f'❌ Erreur lors de l\'envoi: {str(e)}')
        
        return HttpResponseRedirect(
            reverse('admin:core_emailsettings_change', args=[1])
        )

    def has_add_permission(self, request):
        return not EmailSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj, created = EmailSettings.objects.get_or_create(pk=1)
        return HttpResponseRedirect(
            reverse('admin:core_emailsettings_change', args=[obj.pk])
        )


# ============================================
# CONFIGURATION PAIEMENT (Singleton)
# ============================================

@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    """Configuration des paiements"""
    
    fieldsets = (
        ('💳 PayPal', {
            'fields': ('paypal_enabled', 'paypal_mode', 'paypal_client_id', 
                      'paypal_client_secret', 'paypal_webhook_id'),
            'description': '''
            <div class="help">
                <strong>Configuration PayPal:</strong><br>
                1. Connectez-vous sur <a href="https://developer.paypal.com" target="_blank">developer.paypal.com</a><br>
                2. Créez une application dans "Dashboard" > "My Apps & Credentials"<br>
                3. Copiez le Client ID et Secret<br>
                4. Pour tester, utilisez le mode "Sandbox"
            </div>
            ''',
        }),
        ('💳 Stripe', {
            'fields': ('stripe_enabled', 'stripe_mode', 'stripe_public_key', 
                      'stripe_secret_key', 'stripe_webhook_secret'),
            'classes': ('collapse',),
            'description': '''
            <div class="help">
                <strong>Configuration Stripe:</strong><br>
                1. Connectez-vous sur <a href="https://dashboard.stripe.com" target="_blank">dashboard.stripe.com</a><br>
                2. Allez dans "Developers" > "API keys"<br>
                3. Copiez les clés publique et secrète
            </div>
            ''',
        }),
        ('🏦 Virement bancaire', {
            'fields': ('bank_transfer_enabled', 'bank_name', 'bank_account_holder',
                      'bank_iban', 'bank_bic'),
            'classes': ('collapse',),
        }),
        ('💵 Paiement à la livraison', {
            'fields': ('cod_enabled', 'cod_fee'),
            'classes': ('collapse',),
        }),
        ('⚙️ Options', {
            'fields': ('currency',),
        }),
    )

    def has_add_permission(self, request):
        return not PaymentSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj, created = PaymentSettings.objects.get_or_create(pk=1)
        return HttpResponseRedirect(
            reverse('admin:core_paymentsettings_change', args=[obj.pk])
        )


# ============================================
# MÉTHODES DE LIVRAISON (illimitées)
# ============================================

@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    """Gestion des méthodes de livraison"""
    
    list_display = ('name', 'price', 'free_from', 'delivery_estimate', 'is_active', 'order')
    list_editable = ('price', 'free_from', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('order', 'price')

    fieldsets = (
        ('📦 Méthode de livraison', {
            'fields': ('name', 'description'),
        }),
        ('💰 Tarification', {
            'fields': ('price', 'free_from'),
        }),
        ('⏱️ Délais', {
            'fields': ('delivery_days_min', 'delivery_days_max'),
        }),
        ('⚙️ Options', {
            'fields': ('is_active', 'order'),
        }),
    )


# ============================================
# CHAMPS PERSONNALISÉS (illimités)
# ============================================

@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    """Ajoutez autant de champs personnalisés que vous voulez!"""
    
    list_display = ('label', 'name', 'value_preview', 'location', 'icon', 'is_active', 'order')
    list_display_links = ('label', 'name')
    list_editable = ('is_active', 'order')
    list_filter = ('location', 'is_active')
    search_fields = ('name', 'label', 'value')
    ordering = ('location', 'order')

    fieldsets = (
        ('📝 Définition du champ', {
            'fields': ('name', 'label', 'value'),
            'description': 'Créez n\'importe quel champ avec le nom que vous voulez!',
        }),
        ('🎨 Apparence', {
            'fields': ('icon', 'location'),
            'description': 'Icônes Bootstrap: bi-clock, bi-geo-alt, bi-envelope, bi-phone, etc.',
        }),
        ('⚙️ Options', {
            'fields': ('is_active', 'order'),
        }),
    )

    def value_preview(self, obj):
        if len(obj.value) > 50:
            return obj.value[:50] + '...'
        return obj.value
    value_preview.short_description = 'Valeur'


# ============================================
# BANNIÈRES (illimitées)
# ============================================

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    """Gestion des bannières et promotions"""
    
    list_display = ('title', 'banner_type', 'image_preview', 'is_active', 
                    'start_date', 'end_date', 'order')
    list_display_links = ('title',)
    list_editable = ('is_active', 'order')
    list_filter = ('banner_type', 'is_active')
    search_fields = ('title', 'subtitle')
    ordering = ('order', '-start_date')
    date_hierarchy = 'start_date'

    fieldsets = (
        ('📝 Contenu', {
            'fields': ('title', 'subtitle', 'image'),
        }),
        ('🎨 Style', {
            'fields': ('background_color', 'text_color'),
        }),
        ('🔗 Action', {
            'fields': ('button_text', 'button_url'),
        }),
        ('📍 Configuration', {
            'fields': ('banner_type', 'is_active', 'order'),
        }),
        ('📅 Programmation', {
            'fields': ('start_date', 'end_date'),
            'description': 'Laissez vide pour une bannière permanente',
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" height="40" style="object-fit:cover;border-radius:4px;"/>', 
                             obj.image.url)
        return '-'
    image_preview.short_description = 'Aperçu'


# ============================================
# PAGES LÉGALES (illimitées)
# ============================================

@admin.register(LegalPage)
class LegalPageAdmin(admin.ModelAdmin):
    """Gestion des pages légales et de contenu"""
    
    list_display = ('title', 'page_type', 'slug', 'show_in_footer', 'is_active', 'order', 'updated_at')
    list_display_links = ('title',)
    list_editable = ('show_in_footer', 'is_active', 'order')
    list_filter = ('page_type', 'is_active', 'show_in_footer')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('order',)

    fieldsets = (
        ('📄 Page', {
            'fields': ('page_type', 'title', 'slug'),
        }),
        ('📝 Contenu', {
            'fields': ('content',),
            'description': 'Vous pouvez utiliser du HTML',
        }),
        ('🔍 SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',),
        }),
        ('⚙️ Options', {
            'fields': ('is_active', 'show_in_footer', 'order'),
        }),
    )

    class Media:
        js = ('https://cdn.ckeditor.com/4.16.2/standard/ckeditor.js',)


# ============================================
# PERSONNALISATION DU SITE D'ADMIN
# ============================================

admin.site.site_header = '🛍️ Smile Shop - Administration'
admin.site.site_title = 'Smile Shop Admin'
admin.site.index_title = 'Tableau de bord'
