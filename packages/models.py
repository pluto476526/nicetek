from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.contrib.postgres.fields import ArrayField

class PackageCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text='Font Awesome icon class')
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Package Categories'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('packages:category', kwargs={'slug': self.slug})

class Package(models.Model):
    category = models.ForeignKey(PackageCategory, on_delete=models.CASCADE, related_name='packages')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = RichTextField()
    detailed_description = RichTextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Original price if on discount')
    image = models.ImageField(upload_to='packages/')
    gallery = ArrayField(models.URLField(), blank=True, default=list, help_text='Gallery image URLs')
    deliverables = models.JSONField(default=list, help_text='List of deliverables')
    technical_specs = models.JSONField(default=dict, blank=True)
    timeline = models.CharField(max_length=200, help_text='Estimated delivery timeline')
    installation_details = RichTextField(blank=True)
    support_details = RichTextField(blank=True)
    billing_cycle = models.CharField(
        max_length=20,
        choices=[
            ('one_time', 'One-time'),
            ('monthly', 'Monthly'),
            ('annually', 'Annually'),
            ('project', 'Project-based'),
        ],
        default='one_time'
    )

    pricing_type = models.CharField(
        max_length=20,
        choices=[
            ('fixed', 'Fixed Price'),
            ('starting_from', 'Starting From'),
            ('custom', 'Custom Quote'),
        ],
        default='fixed'
    )

    max_devices = models.PositiveIntegerField(null=True, blank=True)
    is_custom_quote = models.BooleanField(default=False)
    warranty = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    is_recommended = models.BooleanField(default=False)
    is_best_value = models.BooleanField(default=False)
    published = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.name} - KSh {self.price:,}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('packages:detail', kwargs={'slug': self.slug})
    
    @property
    def savings(self):
        if self.original_price and self.original_price > self.price:
            return self.original_price - self.price
        return 0

class PackageFeature(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='features')
    icon = models.CharField(max_length=50, help_text='Font Awesome icon class')
    title = models.CharField(max_length=200)
    description = models.TextField()
    included = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.package.name} - {self.title}"

class PackageAddon(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='addons')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    optional = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.package.name} - {self.name}"

class PackageComparison(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='comparisons')
    title = models.CharField(max_length=200)
    features_comparison = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Package Comparisons'
    
    def __str__(self):
        return f"{self.package.name} - {self.title}"
