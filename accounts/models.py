from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model with role-based permissions"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('staff', 'Staff Member'),
        ('client', 'Client'),
        ('guest', 'Guest'),
    ]
    
    username = None  # Remove username field
    email = models.EmailField('Email Address', unique=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True, max_length=500)
    company = models.CharField(max_length=200, blank=True)
    position = models.CharField(max_length=200, blank=True)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
    last_password_change = models.DateTimeField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    two_factor_enabled = models.BooleanField(default=False)
    date_updated = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    def get_short_name(self):
        return self.first_name or self.email.split('@')[0]
    
    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
    
    @property
    def is_staff_member(self):
        return self.role == 'staff' or self.is_staff
    
    @property
    def is_client(self):
        return self.role == 'client'
    
    @property
    def can_access_admin_panel(self):
        return self.is_admin or self.is_staff_member
    
    @property
    def can_manage_users(self):
        return self.is_admin
    
    @property
    def can_manage_content(self):
        return self.is_admin or self.is_staff_member
    
    @property
    def can_manage_clients(self):
        return self.is_admin or self.is_staff_member
    
    @property
    def can_view_reports(self):
        return self.is_admin or self.is_staff_member
    
    @property
    def is_locked(self):
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False
    
    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        # Generate initials-based avatar
        initials = (self.first_name[:1] + self.last_name[:1]).upper() or self.email[:2].upper()
        return f"https://ui-avatars.com/api/?name={initials}&background=0d47a1&color=fff&size=200"
    
    def get_absolute_url(self):
        return reverse('accounts:profile')
    
    def has_permission(self, perm):
        """Check if user has specific permission"""
        permission_map = {
            'manage_users': self.can_manage_users,
            'manage_content': self.can_manage_content,
            'manage_clients': self.can_manage_clients,
            'view_reports': self.can_view_reports,
            'access_admin': self.can_access_admin_panel,
        }
        return permission_map.get(perm, False)


class UserActivity(models.Model):
    """Track user activity for security and analytics"""
    
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('login_failed', 'Login Failed'),
        ('password_change', 'Password Change'),
        ('password_reset', 'Password Reset'),
        ('profile_update', 'Profile Update'),
        ('email_verified', 'Email Verified'),
        ('account_locked', 'Account Locked'),
        ('account_unlocked', 'Account Unlocked'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'User Activities'
    
    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.timestamp}"


class PasswordResetToken(models.Model):
    """Custom password reset tokens for better control"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {'Used' if self.used else 'Active'}"
    
    @property
    def is_expired(self):
        return self.expires_at < timezone.now()
    
    @property
    def is_valid(self):
        return not self.used and not self.is_expired


class EmailVerificationToken(models.Model):
    """Email verification tokens"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_tokens')
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.email} - {'Verified' if self.verified else 'Pending'}"
    
    @property
    def is_expired(self):
        return self.expires_at < timezone.now()
    
    @property
    def is_valid(self):
        return not self.verified and not self.is_expired
