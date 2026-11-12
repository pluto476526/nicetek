from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    path('templates/', views.TemplateListView.as_view(), name='templates'),
    path('templates/create/', views.TemplateCreateView.as_view(), name='template_create'),
    path('campaigns/', views.CampaignListView.as_view(), name='campaigns'),
    path('campaigns/create/', views.CampaignCreateView.as_view(), name='campaign_create'),
    path('campaigns/<int:pk>/send/', views.campaign_send_view, name='campaign_send'),
    path('campaigns/<int:pk>/preview/', views.campaign_preview_view, name='campaign_preview'),
    path('unsubscribe/', views.unsubscribe_view, name='unsubscribe'),
]
