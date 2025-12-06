from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Order, Invoice


@login_required
def order_list(request):
    """Liste des commandes du client"""
    orders = Order.objects.filter(user=request.user)
    return render(request, 'invoicing/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """Détail d'une commande"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'invoicing/order_detail.html', {'order': order})


@login_required
def invoice_list(request):
    """Liste des factures du client"""
    invoices = Invoice.objects.filter(user=request.user)
    return render(request, 'invoicing/invoice_list.html', {'invoices': invoices})


@login_required
def invoice_detail(request, invoice_id):
    """Détail d'une facture"""
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    return render(request, 'invoicing/invoice_detail.html', {'invoice': invoice})


@login_required
def invoice_pdf(request, invoice_id):
    """Télécharger la facture en PDF"""
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    
    # Générer le HTML de la facture
    html_content = render_to_string('invoicing/invoice_pdf.html', {
        'invoice': invoice,
    })
    
    # Pour l'instant, retourner le HTML (le PDF nécessite weasyprint)
    # En production, utiliser weasyprint pour générer le PDF
    response = HttpResponse(html_content, content_type='text/html')
    # response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = f'attachment; filename="facture_{invoice.invoice_number}.pdf"'
    
    return response
