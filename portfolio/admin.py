from django.contrib import admin
from django.utils.html import format_html
from .models import PortfolioCategory, Project, ProjectTestimonial

class ProjectTestimonialInline(admin.TabularInline):
    model = ProjectTestimonial
    extra = 1

@admin.register(PortfolioCategory)
class PortfolioCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'industry', 'featured', 'published', 'completion_date']
    list_filter = ['industry', 'featured', 'published', 'category']
    search_fields = ['title', 'client', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['featured', 'published']
    inlines = [ProjectTestimonialInline]
    
    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;" />', obj.image.url)
        return 'No image'
    preview_image.short_description = 'Image'
