from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.contrib.postgres.fields import ArrayField

class PortfolioCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, help_text='Font Awesome icon class')
    
    class Meta:
        verbose_name_plural = 'Portfolio Categories'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Project(models.Model):
    INDUSTRY_CHOICES = [
        ('school', 'Schools'),
        ('business', 'Businesses'),
        ('airbnb', 'Airbnb/Hostels'),
        ('apartment', 'Apartments'),
        ('office', 'Offices'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(PortfolioCategory, on_delete=models.CASCADE, related_name='projects')
    client = models.CharField(max_length=200)
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES)
    description = RichTextField()
    challenge = RichTextField()
    solution = RichTextField()
    results = RichTextField()
    image = models.ImageField(upload_to='portfolio/')
    gallery = ArrayField(models.URLField(), blank=True, default=list)
    technologies_used = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    website_url = models.URLField(blank=True)
    completion_date = models.DateField()
    featured = models.BooleanField(default=False)
    published = models.BooleanField(default=True)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-completion_date']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('portfolio:detail', kwargs={'slug': self.slug})

class ProjectTestimonial(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='testimonials')
    author = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    content = models.TextField()
    featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-featured']
    
    def __str__(self):
        return f"{self.author} - {self.project.title}"
