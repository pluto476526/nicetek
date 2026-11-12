from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # ===== DASHBOARD =====
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # ===== PACKAGES =====
    path('packages/', views.PackageListView.as_view(), name='package_list'),
    path('packages/create/', views.PackageCreateView.as_view(), name='package_create'),
    path('packages/<int:pk>/', views.PackageDetailView.as_view(), name='package_detail'),
    path('packages/<int:pk>/update/', views.PackageUpdateView.as_view(), name='package_update'),
    path('packages/<int:pk>/delete/', views.PackageDeleteView.as_view(), name='package_delete'),
    
    # ===== SERVICES =====
    path('services/', views.ServiceListView.as_view(), name='service_list'),
    path('services/create/', views.ServiceCreateView.as_view(), name='service_create'),
    path('services/<int:pk>/', views.ServiceDetailView.as_view(), name='service_detail'),
    path('services/<int:pk>/update/', views.ServiceUpdateView.as_view(), name='service_update'),
    path('services/<int:pk>/delete/', views.ServiceDeleteView.as_view(), name='service_delete'),
    
    # ===== PORTFOLIO =====
    path('portfolio/', views.PortfolioListView.as_view(), name='portfolio_list'),
    path('portfolio/create/', views.PortfolioCreateView.as_view(), name='portfolio_create'),
    path('portfolio/<int:pk>/', views.PortfolioDetailView.as_view(), name='portfolio_detail'),
    path('portfolio/<int:pk>/update/', views.PortfolioUpdateView.as_view(), name='portfolio_update'),
    path('portfolio/<int:pk>/delete/', views.PortfolioDeleteView.as_view(), name='portfolio_delete'),
    
    # ===== BLOG =====
    path('blog/', views.BlogListView.as_view(), name='blog_list'),
    path('blog/create/', views.BlogCreateView.as_view(), name='blog_create'),
    path('blog/<int:pk>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path('blog/<int:pk>/update/', views.BlogUpdateView.as_view(), name='blog_update'),
    path('blog/<int:pk>/delete/', views.BlogDeleteView.as_view(), name='blog_delete'),
    
    # ===== CLIENTS =====
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/create/', views.ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('clients/<int:pk>/update/', views.ClientUpdateView.as_view(), name='client_update'),
    path('clients/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),
    
    # ===== PROJECTS =====
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/update/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    path('projects/<int:pk>/complete/', views.ProjectCompleteView.as_view(), name='project_complete'),
    
    # ===== SUPPORT TICKETS =====
    path('tickets/', views.TicketListView.as_view(), name='ticket_list'),
    path('tickets/<int:pk>/', views.TicketDetailView.as_view(), name='ticket_detail'),
    path('tickets/<int:pk>/update/', views.TicketUpdateView.as_view(), name='ticket_update'),
    path('tickets/<int:pk>/delete/', views.TicketDeleteView.as_view(), name='ticket_delete'),
    
    # ===== TESTIMONIALS =====
    path('testimonials/', views.TestimonialListView.as_view(), name='testimonial_list'),
    path('testimonials/create/', views.TestimonialCreateView.as_view(), name='testimonial_create'),
    path('testimonials/<int:pk>/update/', views.TestimonialUpdateView.as_view(), name='testimonial_update'),
    path('testimonials/<int:pk>/delete/', views.TestimonialDeleteView.as_view(), name='testimonial_delete'),
    
    # ===== FAQs =====
    path('faqs/', views.FAQListView.as_view(), name='faq_list'),
    path('faqs/create/', views.FAQCreateView.as_view(), name='faq_create'),
    path('faqs/<int:pk>/update/', views.FAQUpdateView.as_view(), name='faq_update'),
    path('faqs/<int:pk>/delete/', views.FAQDeleteView.as_view(), name='faq_delete'),
    
    # ===== QUOTE REQUESTS =====
    path('quotes/', views.QuoteListView.as_view(), name='quote_list'),
    path('quotes/<int:pk>/', views.QuoteDetailView.as_view(), name='quote_detail'),
    path('quotes/<int:pk>/update/', views.QuoteUpdateView.as_view(), name='quote_update'),
    path('quotes/<int:pk>/delete/', views.QuoteDeleteView.as_view(), name='quote_delete'),
    
    # ===== CONTACT MESSAGES =====
    path('contacts/', views.ContactListView.as_view(), name='contact_list'),
    path('contacts/<int:pk>/', views.ContactDetailView.as_view(), name='contact_detail'),
    path('contacts/<int:pk>/mark-replied/', views.ContactMarkRepliedView.as_view(), name='contact_mark_replied'),
    path('contacts/<int:pk>/delete/', views.ContactDeleteView.as_view(), name='contact_delete'),
    
    # ===== SUBSCRIBERS =====
    path('subscribers/', views.SubscriberListView.as_view(), name='subscriber_list'),
    path('subscribers/export/', views.SubscriberExportView.as_view(), name='subscriber_export'),
    path('subscribers/<int:pk>/delete/', views.SubscriberDeleteView.as_view(), name='subscriber_delete'),
    
    # ===== TEAM =====
    path('team/', views.TeamListView.as_view(), name='team_list'),
    path('team/create/', views.TeamCreateView.as_view(), name='team_create'),
    path('team/<int:pk>/update/', views.TeamUpdateView.as_view(), name='team_update'),
    path('team/<int:pk>/delete/', views.TeamDeleteView.as_view(), name='team_delete'),
]
