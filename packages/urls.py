from django.urls import path
from . import views

app_name = 'packages'

urlpatterns = [
    path('', views.PackageListView.as_view(), name='list'),
    path('category/<slug:slug>/', views.PackageCategoryView.as_view(), name='category'),
    path('compare/', views.PackageCompareView.as_view(), name='compare'),
    path('<slug:slug>/', views.PackageDetailView.as_view(), name='detail'),
]
