from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.BlogListView.as_view(), name='list'),
    path('search/', views.BlogSearchView.as_view(), name='search'),
    path('category/<slug:slug>/', views.BlogCategoryView.as_view(), name='category'),
    path('tag/<str:tag>/', views.BlogTagView.as_view(), name='tag'),
    path('<slug:slug>/', views.BlogDetailView.as_view(), name='detail'),
    path('<slug:slug>/comment/', views.CommentCreateView.as_view(), name='comment'),
]
