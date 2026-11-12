from django.db import models
# from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from accounts.models import User

class Client(models.Model):
    BUSINESS_TYPES = [
        ('sole', 'Sole Proprietorship'),
        ('partnership', 'Partnership'),
        ('company', 'Limited Company'),
        ('ngo', 'NGO'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    company_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    town = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    tax_id = models.CharField(max_length=50, blank=True)
    business_type = models.CharField(max_length=50, choices=BUSINESS_TYPES, default='sole')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.company_name} - {self.user.email}"

class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='subscriptions')
    package = models.ForeignKey('packages.Package', on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, default='mpesa')
    recurring = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.client.company_name} - {self.package.name}"
    
    @property
    def is_active(self):
        return self.status == 'active' and self.end_date >= timezone.now().date()

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=50, unique=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    items = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            prefix = 'INV'
            year = timezone.now().strftime('%Y')
            count = Invoice.objects.filter(created_at__year=timezone.now().year).count() + 1
            self.invoice_number = f"{prefix}-{year}-{count:05d}"
        self.total = self.amount + self.tax
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.invoice_number} - {self.client.company_name}"

class Payment(models.Model):
    METHOD_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('card', 'Card'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50, choices=METHOD_CHOICES)
    reference = models.CharField(max_length=200, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.reference} - {self.amount}"
