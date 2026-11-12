from django.utils import timezone
from django.shortcuts import render
from django.conf import settings
from .models import PageView
import re

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Log page views
        if request.method == 'GET' and not request.path.startswith('/admin') and not request.path.startswith('/static'):
            PageView.objects.create(
                url=request.build_absolute_uri(),
                ip_address=self.get_client_ip(request),
                session_key=request.session.session_key or '',
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                referrer=request.META.get('HTTP_REFERER', '')[:500],
            )
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.path.startswith('/admin') or request.path.startswith('/static'):
            return self.get_response(request)
        
        from .models import SiteSettings
        try:
            settings_obj = SiteSettings.objects.first()
            if settings_obj and settings_obj.maintenance_mode:
                return render(request, 'core/maintenance.html', {
                    'message': settings_obj.maintenance_message
                }, status=503)
        except:
            pass
        
        return self.get_response(request)
