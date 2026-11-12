from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import NewsletterTemplate, NewsletterCampaign, NewsletterAnalytics
from core.models import NewsletterSubscriber

@method_decorator(staff_member_required, name='dispatch')
class TemplateListView(ListView):
    model = NewsletterTemplate
    template_name = 'newsletter/template_list.html'
    context_object_name = 'templates'

@method_decorator(staff_member_required, name='dispatch')
class TemplateCreateView(CreateView):
    model = NewsletterTemplate
    fields = ['name', 'subject', 'content']
    template_name = 'newsletter/template_form.html'
    success_url = reverse_lazy('newsletter:templates')

@method_decorator(staff_member_required, name='dispatch')
class CampaignListView(ListView):
    model = NewsletterCampaign
    template_name = 'newsletter/campaign_list.html'
    context_object_name = 'campaigns'

@method_decorator(staff_member_required, name='dispatch')
class CampaignCreateView(CreateView):
    model = NewsletterCampaign
    fields = ['template', 'subject', 'content']
    template_name = 'newsletter/campaign_form.html'
    success_url = reverse_lazy('newsletter:campaigns')
    
    def form_valid(self, form):
        subscribers = NewsletterSubscriber.objects.filter(is_active=True, confirmed=True)
        form.instance.recipients = [sub.email for sub in subscribers]
        return super().form_valid(form)

@staff_member_required
def campaign_send_view(request, pk):
    campaign = get_object_or_404(NewsletterCampaign, pk=pk)
    if request.method == 'POST':
        campaign.send_campaign()
        messages.success(request, 'Campaign sent successfully!')
        return redirect('newsletter:campaigns')
    return render(request, 'newsletter/campaign_send_confirm.html', {'campaign': campaign})

@staff_member_required
def campaign_preview_view(request, pk):
    campaign = get_object_or_404(NewsletterCampaign, pk=pk)
    return render(request, 'newsletter/campaign_preview.html', {'campaign': campaign})

def unsubscribe_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            subscriber = NewsletterSubscriber.objects.get(email=email)
            subscriber.is_active = False
            subscriber.unsubscribed_date = timezone.now()
            subscriber.save()
            messages.success(request, 'You have been unsubscribed successfully.')
        except NewsletterSubscriber.DoesNotExist:
            messages.error(request, 'Email not found in our subscription list.')
        return redirect('core:home')
    return render(request, 'newsletter/unsubscribe.html')
