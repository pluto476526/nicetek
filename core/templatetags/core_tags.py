from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter
import markdown

register = template.Library()

@register.filter(name='markdown')
@stringfilter
def markdown_filter(value):
    return mark_safe(markdown.markdown(value, extensions=['extra', 'codehilite']))

@register.simple_tag
def get_package_category_icon(category):
    icons = {
        'starter': 'fa-rocket',
        'business': 'fa-building',
        'enterprise': 'fa-crown',
        'apartment': 'fa-building',
        'school': 'fa-graduation-cap',
    }
    return icons.get(category, 'fa-box')

@register.simple_tag
def get_service_icon(service_type):
    icons = {
        'networking': 'fa-wifi',
        'security': 'fa-shield-alt',
        'web': 'fa-code',
        'consulting': 'fa-handshake',
        'maintenance': 'fa-tools',
    }
    return icons.get(service_type, 'fa-cog')

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '')
