from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserActivity, PasswordResetToken, EmailVerificationToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'avatar_preview', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser', 'email_verified']
    search_fields = ['email', 'first_name', 'last_name', 'phone', 'company']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone', 'avatar', 'bio', 'company', 'position')
        }),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 
                      'email_verified', 'two_factor_enabled',
                      'groups', 'user_permissions'),
        }),
        ('Security', {
            'fields': ('failed_login_attempts', 'locked_until', 'last_password_change'),
            'classes': ('collapse',),
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'date_updated'),
            'classes': ('collapse',),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )
    
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;" />',
                obj.avatar.url
            )
        return format_html(
            '<img src="{}" style="width:40px;height:40px;border-radius:50%;" />',
            obj.avatar_url
        )
    avatar_preview.short_description = 'Avatar'


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'ip_address', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__email', 'ip_address', 'description']
    readonly_fields = ['user', 'action', 'ip_address', 'user_agent', 'description', 'timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token_preview', 'created_at', 'expires_at', 'used', 'is_expired_display']
    list_filter = ['used', 'created_at']
    search_fields = ['user__email', 'token']
    readonly_fields = ['token', 'created_at']
    
    def token_preview(self, obj):
        return f"{obj.token[:20]}..."
    token_preview.short_description = 'Token'
    
    def is_expired_display(self, obj):
        if obj.is_expired:
            return format_html('<span style="color:red;">✗ Expired</span>')
        return format_html('<span style="color:green;">✓ Valid</span>')
    is_expired_display.short_description = 'Status'


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token_preview', 'created_at', 'expires_at', 'verified']
    list_filter = ['verified', 'created_at']
    search_fields = ['user__email', 'token']
    
    def token_preview(self, obj):
        return f"{obj.token[:20]}..."
    token_preview.short_description = 'Token'
