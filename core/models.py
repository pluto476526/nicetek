from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import EmailValidator
from django.utils.text import slugify
from ckeditor.fields import RichTextField

class CompanyInfo(models.Model):
    name = models.CharField(max_length=200)
    tagline = models.CharField(max_length=500)
    logo = models.ImageField(upload_to='company/')
    favicon = models.ImageField(upload_to='company/', null=True, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    about_text = RichTextField()
    mission = RichTextField()
    vision = RichTextField()
    values = RichTextField()
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    google_maps_embed = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=200)
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True)
    google_analytics_id = models.CharField(max_length=50, blank=True)
    google_tag_manager_id = models.CharField(max_length=50, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.TextField(blank=True)
    og_image = models.ImageField(upload_to='seo/', null=True, blank=True)
    
    def __str__(self):
        return self.site_name

class Testimonial(models.Model):
    author = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    position = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    rating = models.IntegerField(choices=[(i, f'{i} Stars') for i in range(1, 6)])
    image = models.ImageField(upload_to='testimonials/', null=True, blank=True)
    featured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.author} - {self.rating}★"

class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('packages', 'Packages'),
        ('installation', 'Installation'),
        ('support', 'Support'),
        ('billing', 'Billing & Payment'),
    ]
    
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    question = models.CharField(max_length=500)
    answer = RichTextField()
    order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['category', 'order']
    
    def __str__(self):
        return self.question

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    confirmed = models.BooleanField(default=False)
    token = models.CharField(max_length=100, unique=True)
    subscribed_date = models.DateTimeField(auto_now_add=True)
    unsubscribed_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.email

class ContactMessage(models.Model):
    INQUIRY_TYPES = [
        ('general', 'General Inquiry'),
        ('sales', 'Sales Inquiry'),
        ('support', 'Support'),
        ('quote', 'Request Quote'),
        ('partnership', 'Partnership'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('closed', 'Closed'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    inquiry_type = models.CharField(max_length=50, choices=INQUIRY_TYPES, default='general')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"

class QuoteRequest(models.Model):
    SERVICE_CHOICES = [
        ('networking', 'Networking Solutions'),
        ('security', 'Security Systems'),
        ('web', 'Web Development'),
        ('consulting', 'IT Consulting'),
        ('maintenance', 'Maintenance & Support'),
        ('custom', 'Custom Solution'),
    ]
    
    BUDGET_CHOICES = [
        ('0-50000', 'KSh 0 - 50,000'),
        ('50000-100000', 'KSh 50,000 - 100,000'),
        ('100000-200000', 'KSh 100,000 - 200,000'),
        ('200000-500000', 'KSh 200,000 - 500,000'),
        ('500000+', 'KSh 500,000+'),
    ]
    
    TIMELINE_CHOICES = [
        ('immediate', 'Immediate'),
        ('1-2-weeks', '1-2 Weeks'),
        ('1-month', '1 Month'),
        ('2-3-months', '2-3 Months'),
        ('flexible', 'Flexible'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewing', 'Reviewing'),
        ('quoted', 'Quoted'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    company = models.CharField(max_length=200, blank=True)
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    package = models.ForeignKey('packages.Package', on_delete=models.SET_NULL, null=True, blank=True)
    project_details = models.TextField()
    budget = models.CharField(max_length=50, choices=BUDGET_CHOICES)
    timeline = models.CharField(max_length=50, choices=TIMELINE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.service_type}"

class PageView(models.Model):
    url = models.URLField(max_length=500)
    ip_address = models.GenericIPAddressField()
    session_key = models.CharField(max_length=40, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(max_length=500, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
