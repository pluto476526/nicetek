from django.contrib import admin
from django.utils.html import format_html
from .models import (
    CompanyInfo, SiteSettings, Testimonial, FAQ,
    NewsletterSubscriber, ContactMessage, QuoteRequest, PageView
)

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not CompanyInfo.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['author', 'company', 'rating', 'featured', 'active', 'order']
    list_filter = ['rating', 'featured', 'active']
    search_fields = ['author', 'company', 'content']
    ordering = ['order', '-created_at']
    list_editable = ['order', 'featured', 'active']

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'active', 'order']
    list_filter = ['category', 'active']
    search_fields = ['question', 'answer']
    list_editable = ['order', 'active']

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'confirmed', 'is_active', 'subscribed_date']
    list_filter = ['confirmed', 'is_active']
    search_fields = ['email']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'inquiry_type', 'status', 'created_at']
    list_filter = ['inquiry_type', 'status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'service_type', 'budget', 'status', 'created_at']
    list_filter = ['service_type', 'status', 'budget']
    search_fields = ['name', 'email', 'company', 'project_details']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['url', 'ip_address', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['url', 'ip_address']
    readonly_fields = ['url', 'ip_address', 'session_key', 'user_agent', 'referrer', 'timestamp']
