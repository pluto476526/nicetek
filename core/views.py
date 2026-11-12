from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
import uuid

from .models import (
    CompanyInfo, SiteSettings, Testimonial, FAQ,
    NewsletterSubscriber, ContactMessage, QuoteRequest
)
from .forms import ContactForm, QuoteRequestForm, NewsletterForm, CareerApplicationForm
from packages.models import Package
from services.models import Service
from blog.models import BlogPost
from portfolio.models import Project
from team.models import TeamMember, JobOpening, JobApplication

class HomeView(TemplateView):
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['testimonials'] = Testimonial.objects.filter(active=True, featured=True)[:6]
        context['packages'] = Package.objects.filter(published=True, is_featured=True)[:3]
        context['services'] = Service.objects.filter(published=True)[:4]
        context['blog_posts'] = BlogPost.objects.filter(published=True)[:3]
        context['portfolio_projects'] = Project.objects.filter(published=True, featured=True)[:4]
        context['faqs'] = FAQ.objects.filter(active=True)[:6]
        context['newsletter_form'] = NewsletterForm()
        return context

class ContactView(CreateView):
    model = ContactMessage
    form_class = ContactForm
    template_name = 'core/contact.html'
    success_url = reverse_lazy('contact_success')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Send email notification
        send_mail(
            f'New Contact Message: {form.instance.subject}',
            f"Name: {form.instance.name}\nEmail: {form.instance.email}\nPhone: {form.instance.phone}\n\nMessage:\n{form.instance.message}",
            settings.DEFAULT_FROM_EMAIL,
            [settings.SITE_EMAIL],
            fail_silently=True,
        )
        messages.success(self.request, 'Thank you for contacting us. We will get back to you shortly.')
        return response

class ContactSuccessView(TemplateView):
    template_name = 'core/contact_success.html'

class AboutView(TemplateView):
    template_name = 'core/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['testimonials'] = Testimonial.objects.filter(active=True)[:8]
        context['team_members'] = TeamMember.objects.filter(active=True)
        return context

class FAQView(ListView):
    model = FAQ
    template_name = 'core/faq.html'
    context_object_name = 'faqs'
    
    def get_queryset(self):
        return FAQ.objects.filter(active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Group FAQs by category
        categories = {}
        for faq in self.get_queryset():
            if faq.category not in categories:
                categories[faq.category] = []
            categories[faq.category].append(faq)
        context['faq_categories'] = categories
        return context

class QuoteRequestView(CreateView):
    model = QuoteRequest
    form_class = QuoteRequestForm
    template_name = 'core/quote_request.html'
    success_url = reverse_lazy('quote_success')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['packages'] = Package.objects.filter(published=True)
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Send email notification
        send_mail(
            f'New Quote Request: {form.instance.name}',
            f"""
            Name: {form.instance.name}
            Email: {form.instance.email}
            Phone: {form.instance.phone}
            Company: {form.instance.company}
            Service: {form.instance.get_service_type_display()}
            Budget: {form.instance.get_budget_display()}
            Timeline: {form.instance.get_timeline_display()}
            
            Project Details:
            {form.instance.project_details}
            """,
            settings.DEFAULT_FROM_EMAIL,
            [settings.SITE_EMAIL],
            fail_silently=True,
        )
        messages.success(self.request, 'Your quote request has been submitted successfully. We will contact you within 24 hours.')
        return response

class QuoteSuccessView(TemplateView):
    template_name = 'core/quote_success.html'

class CareersView(TemplateView):
    template_name = 'core/careers.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job_openings'] = JobOpening.objects.filter(active=True)
        return context

class CareerDetailView(DetailView):
    model = JobOpening
    template_name = 'core/career_detail.html'
    context_object_name = 'job'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

class CareerApplyView(CreateView):
    model = JobApplication
    form_class = CareerApplicationForm
    template_name = 'core/career_apply.html'
    success_url = reverse_lazy('careers')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job'] = get_object_or_404(JobOpening, slug=self.kwargs.get('slug'))
        return context
    
    def form_valid(self, form):
        form.instance.job = get_object_or_404(JobOpening, slug=self.kwargs.get('slug'))
        response = super().form_valid(form)
        messages.success(self.request, 'Your application has been submitted successfully.')
        return response

def newsletter_subscribe(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            token = str(uuid.uuid4())
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={'token': token}
            )
            if created:
                messages.success(request, 'Thank you for subscribing to our newsletter!')
            else:
                messages.info(request, 'You are already subscribed to our newsletter.')
        else:
            messages.error(request, 'Please enter a valid email address.')
        return redirect('home')
    return JsonResponse({'error': 'Invalid request'}, status=400)

class LegalView(TemplateView):
    template_name = 'core/legal.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = self.kwargs.get('page', 'privacy')
        return context
