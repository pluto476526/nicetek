from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('dashboard/', views.ClientDashboardView.as_view(), name='dashboard'),
    path('profile/', views.ClientProfileView.as_view(), name='profile'),
    path('subscriptions/', views.SubscriptionListView.as_view(), name='subscriptions'),
    path('invoices/', views.InvoiceListView.as_view(), name='invoices'),
    path('invoices/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),
    path('tickets/', views.TicketListView.as_view(), name='tickets'),
]
