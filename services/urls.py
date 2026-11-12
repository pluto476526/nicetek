from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.ServiceListView.as_view(), name='list'),
    path('category/<slug:slug>/', views.ServiceCategoryView.as_view(), name='category'),
    path('<slug:slug>/', views.ServiceDetailView.as_view(), name='detail'),
]
