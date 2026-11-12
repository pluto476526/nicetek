from django.contrib import admin
from django.utils.html import format_html
from .models import PostCategory, BlogPost, Comment

@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'published', 'featured', 'published_date', 'views_count']
    list_filter = ['category', 'published', 'featured', 'author']
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['published', 'featured']
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'author', 'excerpt', 'content')
        }),
        ('Media', {
            'fields': ('featured_image', 'thumbnail')
        }),
        ('Metadata', {
            'fields': ('tags', 'featured', 'published', 'published_date', 'views_count')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
    
    def preview_image(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit:cover;" />', obj.featured_image.url)
        return 'No image'
    preview_image.short_description = 'Featured Image'
    
    def save_model(self, request, obj, form, change):
        if not obj.published_date and obj.published:
            obj.published_date = timezone.now()
        super().save_model(request, obj, form, change)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'content_preview', 'approved', 'created_at']
    list_filter = ['approved', 'created_at']
    search_fields = ['author', 'email', 'content']
    actions = ['approve_comments', 'disapprove_comments']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'
    
    def approve_comments(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, f'{queryset.count()} comments approved.')
    approve_comments.short_description = 'Approve selected comments'
    
    def disapprove_comments(self, request, queryset):
        queryset.update(approved=False)
        self.message_user(request, f'{queryset.count()} comments disapproved.')
    disapprove_comments.short_description = 'Disapprove selected comments'
