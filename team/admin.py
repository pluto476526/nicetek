from django.contrib import admin
from django.utils.html import format_html
from .models import TeamMember, JobOpening, JobApplication

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'active', 'order']
    list_filter = ['active']
    search_fields = ['name', 'position', 'bio']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order', 'active']

@admin.register(JobOpening)
class JobOpeningAdmin(admin.ModelAdmin):
    list_display = ['title', 'employment_type', 'experience_level', 'location', 'active', 'posted_date']
    list_filter = ['employment_type', 'experience_level', 'active']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'job', 'email', 'status', 'applied_date']
    list_filter = ['status', 'job']
    search_fields = ['full_name', 'email', 'phone']
    list_editable = ['status']
    readonly_fields = ['applied_date', 'updated_at']
