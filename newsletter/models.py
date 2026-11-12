from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from ckeditor.fields import RichTextField

class NewsletterTemplate(models.Model):
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    content = RichTextField()
    html_content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class NewsletterCampaign(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    template = models.ForeignKey(NewsletterTemplate, on_delete=models.CASCADE, related_name='campaigns')
    subject = models.CharField(max_length=200)
    content = RichTextField()
    recipients = models.JSONField(default=list, help_text='List of recipient emails')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    sent_count = models.IntegerField(default=0)
    opened_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.subject} - {self.sent_date or 'Draft'}"
    
    def send_campaign(self):
        from apps.core.models import NewsletterSubscriber
        subscribers = NewsletterSubscriber.objects.filter(is_active=True, confirmed=True)
        emails = [sub.email for sub in subscribers]
        
        for email in emails:
            try:
                send_mail(
                    self.subject,
                    self.content,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    html_message=self.content,
                    fail_silently=True,
                )
                self.sent_count += 1
            except:
                pass
        
        self.status = 'sent'
        self.sent_date = timezone.now()
        self.save()

class NewsletterAnalytics(models.Model):
    campaign = models.ForeignKey(NewsletterCampaign, on_delete=models.CASCADE, related_name='analytics')
    email = models.EmailField()
    opened = models.BooleanField(default=False)
    clicked = models.BooleanField(default=False)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['campaign', 'email']
    
    def __str__(self):
        return f"{self.campaign.subject} - {self.email}"
