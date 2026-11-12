from django.contrib import admin
from django.utils.html import format_html
from .models import Project, Task, ProjectUpdate

class TaskInline(admin.TabularInline):
    model = Task
    extra = 1
    fields = ['name', 'assigned_to', 'status', 'priority', 'due_date']

class ProjectUpdateInline(admin.TabularInline):
    model = ProjectUpdate
    extra = 1
    fields = ['update_text', 'created_by', 'created_at']
    readonly_fields = ['created_at']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'client', 'status', 'priority', 'payment_status', 'created_at']
    list_filter = ['status', 'priority', 'payment_status']
    search_fields = ['name', 'client__company_name', 'description']
    list_editable = ['status', 'priority']
    inlines = [TaskInline, ProjectUpdateInline]
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'assigned_to', 'status', 'due_date']
    list_filter = ['status', 'priority']
    search_fields = ['name', 'description']

@admin.register(ProjectUpdate)
class ProjectUpdateAdmin(admin.ModelAdmin):
    list_display = ['project', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['project__name', 'update_text']
    readonly_fields = ['created_at']
