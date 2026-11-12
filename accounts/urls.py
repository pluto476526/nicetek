from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Profile
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    
    # Password Reset
    path('password/reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password/reset/<str:token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # Admin - User Management
    path('manage/users/', views.UserListView.as_view(), name='user_list'),
    path('manage/users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('manage/users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('manage/users/<int:pk>/update/', views.UserUpdateView.as_view(), name='user_update'),
    path('manage/users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
    path('manage/users/<int:pk>/toggle-active/', views.UserToggleActiveView.as_view(), name='user_toggle_active'),
    path('manage/users/<int:pk>/change-role/', views.UserChangeRoleView.as_view(), name='user_change_role'),
]
