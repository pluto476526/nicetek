from django.conf import settings
from .models import CompanyInfo, SiteSettings
from packages.models import Package
from services.models import Service

def site_context(request):
    try:
        company = CompanyInfo.objects.first()
    except:
        company = None
    
    try:
        site_settings = SiteSettings.objects.first()
    except:
        site_settings = None
    
    return {
        'company': company,
        'site_settings': site_settings,
        'SITE_NAME': settings.SITE_NAME,
        'SITE_PHONE': settings.SITE_PHONE,
        'SITE_EMAIL': settings.SITE_EMAIL,
        'SITE_ADDRESS': settings.SITE_ADDRESS,
    }

def navigation_context(request):
    return {
        'nav_packages': Package.objects.filter(published=True)[:6],
        'nav_services': Service.objects.filter(published=True)[:6],
        # 'nav_categories': Service.CATEGORY_CHOICES,
    }

def notification_context(request):
    if request.user.is_authenticated:
        from support.models import Ticket
        open_tickets = Ticket.objects.filter(client__user=request.user, status__in=['open', 'in_progress']).count()
        return {
            'notifications': {
                'tickets': open_tickets,
            }
        }
    return {'notifications': {}}
