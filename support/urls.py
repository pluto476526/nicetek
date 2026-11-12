from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('', views.TicketListView.as_view(), name='tickets'),
    path('create/', views.TicketCreateView.as_view(), name='ticket_create'),
    path('<int:pk>/', views.TicketDetailView.as_view(), name='ticket_detail'),
    path('<int:pk>/resolve/', views.ticket_resolve_view, name='ticket_resolve'),
    path('<int:ticket_id>/respond/', views.TicketResponseCreateView.as_view(), name='ticket_response'),
    path('knowledge-base/', views.KnowledgeBaseView.as_view(), name='knowledge_base'),
    path('knowledge-base/<slug:slug>/', views.KnowledgeBaseDetailView.as_view(), name='kb_detail'),
    path('knowledge-base/<slug:slug>/helpful/', views.kb_helpful_view, name='kb_helpful'),
]
