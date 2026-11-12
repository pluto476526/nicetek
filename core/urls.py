from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('contact/success/', views.ContactSuccessView.as_view(), name='contact_success'),
    path('quote/', views.QuoteRequestView.as_view(), name='quote'),
    path('quote/success/', views.QuoteSuccessView.as_view(), name='quote_success'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('careers/', views.CareersView.as_view(), name='careers'),
    path('careers/<slug:slug>/', views.CareerDetailView.as_view(), name='career_detail'),
    path('careers/<slug:slug>/apply/', views.CareerApplyView.as_view(), name='career_apply'),
    path('legal/<str:page>/', views.LegalView.as_view(), name='legal'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
]
