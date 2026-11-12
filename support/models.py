from django.db import models
# from django.contrib.auth.models import User
from django.utils import timezone
from ckeditor.fields import RichTextField
from clients.models import Client
from accounts.models import User

class Ticket(models.Model):
    CATEGORY_CHOICES = [
        ('technical', 'Technical Support'),
        ('billing', 'Billing & Payment'),
        ('installation', 'Installation Issue'),
        ('general', 'General Inquiry'),
        ('feature', 'Feature Request'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='tickets')
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=200)
    description = RichTextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.client.company_name} - {self.subject}"
    
    def resolve(self):
        self.status = 'resolved'
        self.resolved_date = timezone.now()
        self.save()

class TicketResponse(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='responses')
    message = RichTextField()
    attachment = models.FileField(upload_to='ticket_attachments/', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.ticket.subject} - {self.created_by.username}"

class KnowledgeBase(models.Model):
    CATEGORY_CHOICES = [
        ('getting_started', 'Getting Started'),
        ('troubleshooting', 'Troubleshooting'),
        ('faq', 'Frequently Asked Questions'),
        ('guides', 'User Guides'),
        ('security', 'Security Tips'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    content = RichTextField()
    tags = models.JSONField(default=list, blank=True)
    views_count = models.IntegerField(default=0)
    helpful_count = models.IntegerField(default=0)
    not_helpful_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Knowledge Base'
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('support:kb_detail', kwargs={'slug': self.slug})
