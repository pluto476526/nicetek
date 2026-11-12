from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Client, Subscription, Invoice, Payment
from support.models import Ticket
from packages.models import Package

class ClientDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'clients/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = Client.objects.get(user=self.request.user)
        context['client'] = client
        context['active_subscriptions'] = Subscription.objects.filter(client=client, status='active')
        context['recent_invoices'] = Invoice.objects.filter(client=client).order_by('-created_at')[:5]
        context['open_tickets'] = Ticket.objects.filter(client=client, status__in=['open', 'in_progress'])
        context['total_invoices'] = Invoice.objects.filter(client=client).count()
        context['total_paid'] = Invoice.objects.filter(client=client, status='paid').count()
        return context

class ClientProfileView(LoginRequiredMixin, UpdateView):
    model = Client
    fields = ['company_name', 'phone', 'address', 'town', 'county', 'business_type']
    template_name = 'clients/profile.html'
    success_url = reverse_lazy('clients:dashboard')
    
    def get_object(self):
        print("user", self.request.user, flush="true")
        return Client.objects.get(user=self.request.user)

class SubscriptionListView(LoginRequiredMixin, ListView):
    model = Subscription
    template_name = 'clients/subscriptions.html'
    context_object_name = 'subscriptions'
    
    def get_queryset(self):
        client = Client.objects.get(user=self.request.user)
        return Subscription.objects.filter(client=client)

class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'clients/invoices.html'
    context_object_name = 'invoices'
    paginate_by = 10
    
    def get_queryset(self):
        client = Client.objects.get(user=self.request.user)
        return Invoice.objects.filter(client=client).order_by('-created_at')

class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'clients/invoice_detail.html'
    context_object_name = 'invoice'
    
    def get_queryset(self):
        client = Client.objects.get(user=self.request.user)
        return Invoice.objects.filter(client=client)

class TicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'clients/tickets.html'
    context_object_name = 'tickets'
    
    def get_queryset(self):
        client = Client.objects.get(user=self.request.user)
        return Ticket.objects.filter(client=client).order_by('-created_at')
