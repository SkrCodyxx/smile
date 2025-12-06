from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Order, OrderItem, Invoice, InvoiceItem, Customer


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_sku', 'quantity', 'unit_price', 'total_price']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user_display', 'status', 'payment_status', 'total_display', 
                    'items_count', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Commande', {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        ('Montants', {
            'fields': ('subtotal', 'tax_amount', 'shipping_amount', 'discount_amount', 'total')
        }),
        ('Adresses', {
            'fields': ('shipping_address', 'billing_address'),
            'classes': ('collapse',)
        }),
        ('Livraison', {
            'fields': ('tracking_number', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered', 'generate_invoice']

    def user_display(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name} ({obj.user.email})"
        return "Client supprimé"
    user_display.short_description = 'Client'

    def total_display(self, obj):
        return format_html('<strong>{} €</strong>', obj.total)
    total_display.short_description = 'Total'

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Articles'

    @admin.action(description="✅ Marquer comme confirmée")
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')

    @admin.action(description="🚚 Marquer comme expédiée")
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped', shipped_at=timezone.now())

    @admin.action(description="✔️ Marquer comme livrée")
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered', delivered_at=timezone.now())

    @admin.action(description="📄 Générer une facture")
    def generate_invoice(self, request, queryset):
        for order in queryset:
            if not hasattr(order, 'invoice') or order.invoice is None:
                invoice = Invoice.objects.create(
                    order=order,
                    user=order.user,
                    subtotal=order.subtotal,
                    tax_amount=order.tax_amount,
                    total=order.total,
                    status='draft'
                )
                # Créer les lignes de facture
                for item in order.items.all():
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        description=item.product_name,
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                        total_price=item.total_price
                    )
                self.message_user(request, f"Facture {invoice.invoice_number} créée pour {order.order_number}")


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ['description', 'quantity', 'unit_price', 'total_price']
    readonly_fields = ['total_price']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'user_display', 'order_link', 'status_display', 
                    'total_display', 'issue_date', 'due_date', 'is_overdue_display']
    list_filter = ['status', 'issue_date', 'due_date']
    search_fields = ['invoice_number', 'user__email', 'order__order_number']
    readonly_fields = ['invoice_number', 'created_at', 'updated_at']
    inlines = [InvoiceItemInline]
    date_hierarchy = 'issue_date'
    
    fieldsets = (
        ('Facture', {
            'fields': ('invoice_number', 'order', 'user', 'status')
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date', 'paid_at')
        }),
        ('Montants', {
            'fields': ('subtotal', 'tax_rate', 'tax_amount', 'total')
        }),
        ('Informations', {
            'fields': ('notes', 'payment_terms'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_sent', 'mark_as_paid']

    def user_display(self, obj):
        if obj.user:
            return obj.user.email
        return "-"
    user_display.short_description = 'Client'

    def order_link(self, obj):
        if obj.order:
            url = reverse('admin:invoicing_order_change', args=[obj.order.id])
            return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
        return "-"
    order_link.short_description = 'Commande'

    def status_display(self, obj):
        colors = {
            'draft': '#6c757d',
            'sent': '#17a2b8',
            'paid': '#28a745',
            'overdue': '#dc3545',
            'cancelled': '#6c757d',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_display.short_description = 'Statut'

    def total_display(self, obj):
        return format_html('<strong>{} €</strong>', obj.total)
    total_display.short_description = 'Total'

    def is_overdue_display(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: red;">⚠️ En retard</span>')
        return format_html('<span style="color: green;">✓</span>')
    is_overdue_display.short_description = 'Retard'

    @admin.action(description="📧 Marquer comme envoyée")
    def mark_as_sent(self, request, queryset):
        queryset.update(status='sent')

    @admin.action(description="✅ Marquer comme payée")
    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid', paid_at=timezone.now())


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'phone', 'city', 'orders_count', 'total_spent']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'company', 'phone']
    list_filter = ['country', 'city']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Entreprise', {
            'fields': ('company', 'siret', 'vat_number')
        }),
        ('Contact', {
            'fields': ('phone', 'address', 'city', 'postal_code', 'country')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )

    def orders_count(self, obj):
        return Order.objects.filter(user=obj.user).count()
    orders_count.short_description = 'Commandes'

    def total_spent(self, obj):
        from django.db.models import Sum
        total = Order.objects.filter(user=obj.user, payment_status='paid').aggregate(Sum('total'))['total__sum']
        return f"{total or 0} €"
    total_spent.short_description = 'Total dépensé'
