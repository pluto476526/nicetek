from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import (
    View, TemplateView, FormView, CreateView, UpdateView, DetailView, ListView
)
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from datetime import timedelta

from .models import User, UserActivity, PasswordResetToken, EmailVerificationToken
from .forms import (
    SignUpForm, LoginForm, ProfileUpdateForm, CustomPasswordChangeForm,
    CustomPasswordResetForm, CustomSetPasswordForm, AdminUserCreateForm
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_activity(user, action, request=None, description=''):
    """Log user activity"""
    ip = get_client_ip(request) if request else None
    user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
    UserActivity.objects.create(
        user=user,
        action=action,
        ip_address=ip,
        user_agent=user_agent[:500],
        description=description
    )


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

class SignUpView(View):
    """User registration"""
    template_name = 'accounts/signup.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:home')
        form = SignUpForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            
            # Log activity
            log_activity(user, 'login', request, 'Account created')
            
            # Send welcome email
            try:
                send_mail(
                    'Welcome to Nicetek Kenya!',
                    f'Hi {user.first_name},\n\n'
                    f'Welcome to Nicetek Kenya! Your account has been created successfully.\n\n'
                    f'You can now log in and access all our services.\n\n'
                    f'Best regards,\nNicetek Kenya Team',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True,
                )
            except Exception:
                pass
            
            # Log the user in
            login(request, user)
            messages.success(request, f'Welcome {user.first_name}! Your account has been created.')
            return redirect('core:home')
        
        return render(request, self.template_name, {'form': form})


class LoginView(View):
    """User login"""
    template_name = 'accounts/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:home')
        form = LoginForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Log activity
            log_activity(user, 'login', request, 'Successful login')
            
            # Handle remember me
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            
            messages.success(request, f'Welcome back, {user.get_short_name()}!')
            
            # Redirect to next or appropriate page
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            
            if user.can_access_admin_panel:
                return redirect('admin_panel:dashboard')
            return redirect('core:home')
        
        # Log failed attempt
        email = request.POST.get('username', '')
        try:
            user = User.objects.get(email__iexact=email)
            log_activity(user, 'login_failed', request, 'Failed login attempt')
        except User.DoesNotExist:
            pass
        
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    """User logout"""
    
    def get(self, request):
        return self.post(request)
    
    def post(self, request):
        if request.user.is_authenticated:
            log_activity(request.user, 'logout', request)
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
        return redirect('core:home')


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile page"""
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['activities'] = self.request.user.activities.all()[:10]
        return context


class ProfileUpdateView(LoginRequiredMixin, View):
    """Update user profile"""
    template_name = 'accounts/profile_edit.html'
    
    def get(self, request):
        form = ProfileUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'profile_update', request)
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        return render(request, self.template_name, {'form': form})


class PasswordChangeView(LoginRequiredMixin, View):
    """Change password"""
    template_name = 'accounts/password_change.html'
    
    def get(self, request):
        form = CustomPasswordChangeForm(user=request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            log_activity(user, 'password_change', request)
            messages.success(request, 'Password changed successfully!')
            return redirect('accounts:profile')
        return render(request, self.template_name, {'form': form})


class PasswordResetView(View):
    """Request password reset"""
    template_name = 'accounts/password_reset.html'
    
    def get(self, request):
        form = CustomPasswordResetForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            try:
                user = User.objects.get(email__iexact=email)
                
                # Create reset token
                token = get_random_string(64)
                PasswordResetToken.objects.create(
                    user=user,
                    token=token,
                    expires_at=timezone.now() + timedelta(hours=24),
                    ip_address=get_client_ip(request)
                )
                
                # Send email
                reset_url = request.build_absolute_uri(
                    reverse('accounts:password_reset_confirm', kwargs={'token': token})
                )
                
                send_mail(
                    'Password Reset - Nicetek Kenya',
                    f'Hi {user.first_name},\n\n'
                    f'You requested a password reset. Click the link below to reset your password:\n\n'
                    f'{reset_url}\n\n'
                    f'This link expires in 24 hours.\n\n'
                    f'If you didn\'t request this, ignore this email.\n\n'
                    f'Best regards,\nNicetek Kenya Team',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True,
                )
                
                log_activity(user, 'password_reset', request, 'Password reset requested')
                messages.success(request, 'Password reset link has been sent to your email.')
                return redirect('accounts:login')
                
            except User.DoesNotExist:
                # Don't reveal whether email exists
                messages.success(request, 'If an account exists with that email, we\'ve sent a reset link.')
                return redirect('accounts:login')
        
        return render(request, self.template_name, {'form': form})


class PasswordResetConfirmView(View):
    """Confirm password reset"""
    template_name = 'accounts/password_reset_confirm.html'
    
    def get_token(self, token_str):
        try:
            return PasswordResetToken.objects.get(token=token_str)
        except PasswordResetToken.DoesNotExist:
            return None
    
    def get(self, request, token):
        reset_token = self.get_token(token)
        if not reset_token or not reset_token.is_valid:
            messages.error(request, 'Invalid or expired reset link.')
            return redirect('accounts:password_reset')
        
        form = CustomSetPasswordForm(user=reset_token.user)
        return render(request, self.template_name, {'form': form, 'token': token})
    
    def post(self, request, token):
        reset_token = self.get_token(token)
        if not reset_token or not reset_token.is_valid:
            messages.error(request, 'Invalid or expired reset link.')
            return redirect('accounts:password_reset')
        
        form = CustomSetPasswordForm(user=reset_token.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            reset_token.used = True
            reset_token.save()
            
            log_activity(user, 'password_change', request, 'Password reset completed')
            messages.success(request, 'Password reset successfully! You can now log in.')
            return redirect('accounts:login')
        
        return render(request, self.template_name, {'form': form, 'token': token})


# ============================================================================
# ADMIN USER MANAGEMENT VIEWS
# ============================================================================

class AdminRequiredMixin(LoginRequiredMixin):
    """Mixin to ensure user has admin panel access"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.can_access_admin_panel:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('core:home')
        return super().dispatch(request, *args, **kwargs)


class UserListView(AdminRequiredMixin, ListView):
    """Admin: List all users"""
    model = User
    template_name = 'accounts/admin/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = User.objects.all()
        search = self.request.GET.get('search')
        role = self.request.GET.get('role')
        status = self.request.GET.get('status')
        
        if search:
            queryset = queryset.filter(
                models.Q(email__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(company__icontains=search)
            )
        if role:
            queryset = queryset.filter(role=role)
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role_choices'] = User.ROLE_CHOICES
        context['active_page'] = 'users'
        context['total_users'] = User.objects.count()
        context['admin_count'] = User.objects.filter(role='admin').count()
        context['staff_count'] = User.objects.filter(role='staff').count()
        context['client_count'] = User.objects.filter(role='client').count()
        return context


class UserDetailView(AdminRequiredMixin, DetailView):
    """Admin: User details"""
    model = User
    template_name = 'accounts/admin/user_detail.html'
    context_object_name = 'user_obj'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'users'
        context['activities'] = self.object.activities.all()[:20]
        return context


class UserCreateView(AdminRequiredMixin, CreateView):
    """Admin: Create user"""
    model = User
    form_class = AdminUserCreateForm
    template_name = 'accounts/admin/user_form.html'
    success_url = reverse_lazy('accounts:user_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'users'
        context['title'] = 'Create User'
        context['button_text'] = 'Create User'
        return context
    
    def form_valid(self, form):
        user = form.save()
        log_activity(self.request.user, 'profile_update', self.request, 
                     f'Created user: {user.email}')
        messages.success(self.request, f'User "{user.email}" created successfully!')
        return super().form_valid(form)


class UserUpdateView(AdminRequiredMixin, UpdateView):
    """Admin: Update user"""
    model = User
    form_class = AdminUserCreateForm
    template_name = 'accounts/admin/user_form.html'
    success_url = reverse_lazy('accounts:user_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'users'
        context['title'] = 'Update User'
        context['button_text'] = 'Update User'
        return context
    
    def form_valid(self, form):
        user = form.save()
        log_activity(self.request.user, 'profile_update', self.request,
                     f'Updated user: {user.email}')
        messages.success(self.request, f'User "{user.email}" updated successfully!')
        return super().form_valid(form)


class UserDeleteView(AdminRequiredMixin, View):
    """Admin: Delete user"""
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        
        if user == request.user:
            messages.error(request, 'You cannot delete your own account.')
            return redirect('accounts:user_list')
        
        if user.is_superuser and not request.user.is_superuser:
            messages.error(request, 'You cannot delete a superuser.')
            return redirect('accounts:user_list')
        
        email = user.email
        user.delete()
        messages.success(request, f'User "{email}" deleted successfully!')
        return redirect('accounts:user_list')


class UserToggleActiveView(AdminRequiredMixin, View):
    """Admin: Toggle user active status"""
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        
        if user == request.user:
            return JsonResponse({'error': 'Cannot toggle your own status'}, status=400)
        
        user.is_active = not user.is_active
        user.save()
        
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User "{user.email}" {status} successfully!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'is_active': user.is_active})
        return redirect('accounts:user_list')


class UserChangeRoleView(AdminRequiredMixin, View):
    """Admin: Change user role"""
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        new_role = request.POST.get('role')
        
        if new_role not in [r[0] for r in User.ROLE_CHOICES]:
            messages.error(request, 'Invalid role.')
            return redirect('accounts:user_detail', pk=pk)
        
        if user == request.user and new_role != 'admin':
            messages.error(request, 'You cannot change your own role.')
            return redirect('accounts:user_detail', pk=pk)
        
        old_role = user.role
        user.role = new_role
        user.save()
        
        messages.success(request, f'User role changed from {old_role} to {new_role}.')
        return redirect('accounts:user_detail', pk=pk)
