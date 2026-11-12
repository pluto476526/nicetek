from django.contrib import admin
from django.utils.html import format_html
from .models import Ticket, TicketResponse, KnowledgeBase

class TicketResponseInline(admin.TabularInline):
    model = TicketResponse
    extra = 1
    fields = ['message', 'created_by', 'created_at']
    readonly_fields = ['created_at']

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['subject', 'client', 'category', 'status', 'priority', 'created_at']
    list_filter = ['category', 'status', 'priority', 'created_at']
    search_fields = ['subject', 'description', 'client__company_name']
    list_editable = ['status', 'priority']
    inlines = [TicketResponseInline]
    readonly_fields = ['created_at', 'updated_at']

@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'views_count', 'helpful_count', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'content', 'tags']
    prepopulated_fields = {'slug': ('title',)}
