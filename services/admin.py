from django.contrib import admin
from django.utils.html import format_html
from .models import ServiceCategory, Service, ServiceFeature, ServiceFAQ

class ServiceFeatureInline(admin.TabularInline):
    model = ServiceFeature
    extra = 1

class ServiceFAQInline(admin.TabularInline):
    model = ServiceFAQ
    extra = 1

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'starting_price', 'is_featured', 'published', 'order']
    list_filter = ['category', 'is_featured', 'published']
    search_fields = ['name', 'short_description', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'is_featured', 'published']
    inlines = [ServiceFeatureInline, ServiceFAQInline]
    
    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;" />', obj.image.url)
        return 'No image'
    preview_image.short_description = 'Image'
