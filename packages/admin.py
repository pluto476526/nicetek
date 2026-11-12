from django.contrib import admin
from django.utils.html import format_html
from .models import PackageCategory, Package, PackageFeature, PackageAddon, PackageComparison

class PackageFeatureInline(admin.TabularInline):
    model = PackageFeature
    extra = 1

class PackageAddonInline(admin.TabularInline):
    model = PackageAddon
    extra = 1

@admin.register(PackageCategory)
class PackageCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order']

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_featured', 'is_recommended', 'published', 'order']
    list_filter = ['category', 'is_featured', 'is_recommended', 'published']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'price', 'is_featured', 'is_recommended', 'published']
    inlines = [PackageFeatureInline, PackageAddonInline]
    
    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;" />', obj.image.url)
        return 'No image'
    preview_image.short_description = 'Image'

@admin.register(PackageComparison)
class PackageComparisonAdmin(admin.ModelAdmin):
    list_display = ['package', 'title', 'created_at']
    search_fields = ['package__name', 'title']
