from django.contrib import admin
from .models import NewsletterTemplate, NewsletterCampaign, NewsletterAnalytics

@admin.register(NewsletterTemplate)
class NewsletterTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'created_at']
    search_fields = ['name', 'subject']

@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(admin.ModelAdmin):
    list_display = ['subject', 'status', 'sent_count', 'sent_date']
    list_filter = ['status', 'sent_date']
    search_fields = ['subject']

@admin.register(NewsletterAnalytics)
class NewsletterAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'email', 'opened', 'clicked', 'created_at']
    list_filter = ['opened', 'clicked']
    search_fields = ['email']
