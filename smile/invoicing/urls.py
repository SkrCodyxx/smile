from django.urls import path
from . import views

app_name = 'invoicing'

urlpatterns = [
    path('orders/', views.order_list, name='order_list'),
    path('orders/<uuid:order_id>/', views.order_detail, name='order_detail'),
    path('', views.invoice_list, name='invoice_list'),
    path('<uuid:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('<uuid:invoice_id>/pdf/', views.invoice_pdf, name='invoice_pdf'),
]
