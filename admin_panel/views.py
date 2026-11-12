from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, 
    TemplateView, View
)
from django.urls import reverse_lazy, reverse
from django.db import transaction
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
import csv

from packages.models import Package, PackageCategory
from services.models import Service, ServiceCategory
from portfolio.models import Project as PortfolioProject, PortfolioCategory
from blog.models import BlogPost, PostCategory
from clients.models import Client
from projects.models import Project as ClientProject
from support.models import Ticket
from core.models import (
    Testimonial, FAQ, ContactMessage, QuoteRequest, NewsletterSubscriber
)
from team.models import TeamMember


# ============================================================================
# BASE MIXIN
# ============================================================================

class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure user has admin panel access"""
    
    def test_func(self):
        return (self.request.user.is_authenticated and 
                self.request.user.can_access_admin_panel)
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.error(self.request, 'Please log in to access the admin panel.')
            return redirect(f"{reverse('accounts:login')}?next={self.request.path}")
        messages.error(self.request, 'You do not have permission to access the admin panel.')
        return redirect('core:home')

# ============================================================================
# DASHBOARD
# ============================================================================

class DashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'package_count': Package.objects.count(),
            'published_packages': Package.objects.filter(published=True).count(),
            'service_count': Service.objects.count(),
            'portfolio_count': PortfolioProject.objects.count(),
            'blog_count': BlogPost.objects.count(),
            'client_count': Client.objects.count(),
            'active_clients': Client.objects.filter(user__is_active=True).count(),
            'project_count': ClientProject.objects.count(),
            'in_progress_projects': ClientProject.objects.filter(status='in_progress').count(),
            'ticket_count': Ticket.objects.count(),
            'open_tickets': Ticket.objects.filter(status__in=['open', 'in_progress']).count(),
            'testimonial_count': Testimonial.objects.count(),
            'faq_count': FAQ.objects.count(),
            'quote_count': QuoteRequest.objects.count(),
            'pending_quotes': QuoteRequest.objects.filter(status='pending').count(),
            'contact_count': ContactMessage.objects.count(),
            'unread_messages': ContactMessage.objects.filter(status='new').count(),
            'subscriber_count': NewsletterSubscriber.objects.filter(is_active=True).count(),
            'team_count': TeamMember.objects.filter(active=True).count(),
            'draft_blog_posts': BlogPost.objects.filter(published=False).count(),
            'active_page': 'dashboard',
        })
        return context


# ============================================================================
# PACKAGES
# ============================================================================

class PackageListView(AdminRequiredMixin, ListView):
    model = Package
    template_name = 'admin_panel/packages/list.html'
    context_object_name = 'packages'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Package.objects.all()
        search = self.request.GET.get('search')
        category = self.request.GET.get('category')
        status = self.request.GET.get('status')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        if category:
            queryset = queryset.filter(category_id=category)
        if status == 'published':
            queryset = queryset.filter(published=True)
        elif status == 'draft':
            queryset = queryset.filter(published=False)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': PackageCategory.objects.all(),
            'active_page': 'packages',
        })
        return context


class PackageCreateView(AdminRequiredMixin, CreateView):
    model = Package
    fields = ['name', 'category', 'description', 'detailed_description', 'price', 
              'original_price', 'image', 'timeline', 'deliverables', 'published', 
              'is_featured', 'is_recommended', 'is_best_value']
    template_name = 'admin_panel/packages/create.html'
    success_url = reverse_lazy('admin_panel:package_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': PackageCategory.objects.all(),
            'title': 'Create Package',
            'subtitle': 'Add a new service package',
            'active_page': 'packages',
        })
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Package "{form.instance.name}" created successfully!')
        return super().form_valid(form)


class PackageDetailView(AdminRequiredMixin, DetailView):
    model = Package
    template_name = 'admin_panel/packages/detail.html'
    context_object_name = 'package'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'packages'
        return context


class PackageUpdateView(AdminRequiredMixin, UpdateView):
    model = Package
    fields = ['name', 'category', 'description', 'detailed_description', 'price', 
              'original_price', 'image', 'timeline', 'deliverables', 'published', 
              'is_featured', 'is_recommended', 'is_best_value']
    template_name = 'admin_panel/packages/create.html'
    success_url = reverse_lazy('admin_panel:package_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': PackageCategory.objects.all(),
            'title': 'Update Package',
            'subtitle': f'Editing "{self.object.name}"',
            'active_page': 'packages',
        })
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Package "{form.instance.name}" updated successfully!')
        return super().form_valid(form)


class PackageDeleteView(AdminRequiredMixin, DeleteView):
    model = Package
    template_name = 'admin_panel/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:package_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'object_type': 'Package',
            'object_name': self.object.name,
            'cancel_url': reverse_lazy('admin_panel:package_list'),
            'active_page': 'packages',
        })
        return context
    
    def form_valid(self, form):
        obj = self.get_object()
        messages.success(self.request, f'Package "{obj.name}" deleted successfully!')
        return super().form_valid(form)


# ============================================================================
# SERVICES
# ============================================================================

class ServiceListView(AdminRequiredMixin, ListView):
    model = Service
    template_name = 'admin_panel/services/list.html'
    context_object_name = 'services'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Service.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(short_description__icontains=search)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'services'
        return context


class ServiceCreateView(AdminRequiredMixin, CreateView):
    model = Service
    fields = ['name', 'category', 'short_description', 'description', 
              'detailed_description', 'icon', 'image', 'starting_price', 
              'published', 'is_featured']
    template_name = 'admin_panel/services/create.html'
    success_url = reverse_lazy('admin_panel:service_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': ServiceCategory.objects.all(),
            'title': 'Create Service',
            'subtitle': 'Add a new service',
            'active_page': 'services',
        })
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Service "{form.instance.name}" created successfully!')
        return super().form_valid(form)


class ServiceDetailView(AdminRequiredMixin, DetailView):
    model = Service
    template_name = 'admin_panel/services/detail.html'
    context_object_name = 'service'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'services'
        return context


class ServiceUpdateView(AdminRequiredMixin, UpdateView):
    model = Service
    fields = ['name', 'category', 'short_description', 'description', 
              'detailed_description', 'icon', 'image', 'starting_price', 
              'published', 'is_featured']
    template_name = 'admin_panel/services/create.html'
    success_url = reverse_lazy('admin_panel:service_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': ServiceCategory.objects.all(),
            'title': 'Update Service',
            'subtitle': f'Editing "{self.object.name}"',
            'active_page': 'services',
        })
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Service "{form.instance.name}" updated successfully!')
        return super().form_valid(form)


class ServiceDeleteView(AdminRequiredMixin, DeleteView):
    model = Service
    template_name = 'admin_panel/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:service_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'object_type': 'Service',
            'object_name': self.object.name,
            'cancel_url': reverse_lazy('admin_panel:service_list'),
            'active_page': 'services',
        })
        return context
    
    def form_valid(self, form):
        obj = self.get_object()
        messages.success(self.request, f'Service "{obj.name}" deleted successfully!')
        return super().form_valid(form)


# ============================================================================
# PORTFOLIO
# ============================================================================

class PortfolioListView(AdminRequiredMixin, ListView):
    model = PortfolioProject
    template_name = 'admin_panel/portfolio/list.html'
    context_object_name = 'projects'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = PortfolioProject.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(client__icontains=search)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'portfolio'
        return context


class PortfolioCreateView(AdminRequiredMixin, CreateView):
    model = PortfolioProject
    fields = ['title', 'category', 'client', 'industry', 'description', 'challenge',
              'solution', 'results', 'image', 'technologies_used', 'website_url',
              'completion_date', 'featured', 'published']
    template_name = 'admin_panel/portfolio/create.html'
    success_url = reverse_lazy('admin_panel:portfolio_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': PortfolioCategory.objects.all(),
            'title': 'Create Portfolio Project',
            'subtitle': 'Add a new portfolio project',
            'active_page': 'portfolio',
        })
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Project "{form.instance.title}" created successfully!')
        return super().form_valid(form)


class PortfolioDetailView(AdminRequiredMixin, DetailView):
    model = PortfolioProject
    template_name = 'admin_panel/portfolio/detail.html'
    context_object_name = 'project'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'portfolio'
        return context


class PortfolioUpdateView(AdminRequiredMixin, UpdateView):
    model = PortfolioProject
    fields = ['title', 'category', 'client', 'industry', 'description', 'challenge',
              'solution', 'results', 'image', 'technologies_used', 'website_url',
              'completion_date', 'featured', 'published']
    template_name = 'admin_panel/portfolio/create.html'
    success_url = reverse_lazy('admin_panel:portfolio_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': PortfolioCategory.objects.all(),
            'title': 'Update Portfolio Project',
            'subtitle': f'Editing "{self.object.title}"',
            'active_page': 'portfolio',
        })
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Project "{form.instance.title}" updated successfully!')
        return super().form_valid(form)


class PortfolioDeleteView(AdminRequiredMixin, DeleteView):
    model = PortfolioProject
    template_name = 'admin_panel/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:portfolio_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'object_type': 'Portfolio Project',
            'object_name': self.object.title,
            'cancel_url': reverse_lazy('admin_panel:portfolio_list'),
            'active_page': 'portfolio',
        })
        return context
    
    def form_valid(self, form):
        obj = self.get_object()
        messages.success(self.request, f'Project "{obj.title}" deleted successfully!')
        return super().form_valid(form)


# ============================================================================
# BLOG
# ============================================================================

class BlogListView(AdminRequiredMixin, ListView):
    model = BlogPost
    template_name = 'admin_panel/blog/list.html'
    context_object_name = 'posts'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = BlogPost.objects.all()
        search = self.request.GET.get('search')
        category = self.request.GET.get('category')
        status = self.request.GET.get('status')
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(excerpt__icontains=search)
            )
        if category:
            queryset = queryset.filter(category_id=category)
        if status == 'published':
            queryset = queryset.filter(published=True)
        elif status == 'draft':
            queryset = queryset.filter(published=False)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': PostCategory.objects.all(),
            'active_page': 'blog',
        })
        return context


class BlogCreateView(AdminRequiredMixin, CreateView):
    model = BlogPost
    fields = ['title', 'category', 'excerpt', 'content', 'featured_image', 
              'thumbnail', 'tags', 'published', 'featured', 'published_date']
    template_name = 'admin_panel/blog/create.html'
    success_url = reverse_lazy('admin_panel:blog_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': PostCategory.objects.all(),
            'title': 'Create Blog Post',
            'subtitle': 'Add a new blog post',
            'active_page': 'blog',
        })
        return context
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        if form.instance.published and not form.instance.published_date:
            form.instance.published_date = timezone.now()
        messages.success(self.request, f'Blog post "{form.instance.title}" created successfully!')
        return super().form_valid(form)


class BlogDetailView(AdminRequiredMixin, DetailView):
    model = BlogPost
    template_name = 'admin_panel/blog/detail.html'
    context_object_name = 'post'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'blog'
        return context


class BlogUpdateView(AdminRequiredMixin, UpdateView):
    model = BlogPost
    fields = ['title', 'category', 'excerpt', 'content', 'featured_image', 
              'thumbnail', 'tags', 'published', 'featured', 'published_date']
    template_name = 'admin_panel/blog/create.html'
    success_url = reverse_lazy('admin_panel:blog_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': PostCategory.objects.all(),
            'title': 'Update Blog Post',
            'subtitle': f'Editing "{self.object.title}"',
            'active_page': 'blog',
        })
        return context
    
    def form_valid(self, form):
        if form.instance.published and not form.instance.published_date:
            form.instance.published_date = timezone.now()
        messages.success(self.request, f'Blog post "{form.instance.title}" updated successfully!')
        return super().form_valid(form)


class BlogDeleteView(AdminRequiredMixin, DeleteView):
    model = BlogPost
    template_name = 'admin_panel/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:blog_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'object_type': 'Blog Post',
            'object_name': self.object.title,
            'cancel_url': reverse_lazy('admin_panel:blog_list'),
            'active_page': 'blog',
        })
        return context
    
    def form_valid(self, form):
        obj = self.get_object()
        messages.success(self.request, f'Blog post "{obj.title}" deleted successfully!')
        return super().form_valid(form)


# ============================================================================
# CLIENTS
# ============================================================================

class ClientListView(AdminRequiredMixin, ListView):
    model = Client
    template_name = 'admin_panel/clients/list.html'
    context_object_name = 'clients'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Client.objects.select_related('user').all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(company_name__icontains=search) |
                Q(user__email__icontains=search) |
                Q(phone__icontains=search)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'clients'
        return context


class ClientCreateView(AdminRequiredMixin, CreateView):
    model = Client
    fields = ['company_name', 'phone', 'address', 'town', 'county', 
              'tax_id', 'business_type']
    template_name = 'admin_panel/clients/create.html'
    success_url = reverse_lazy('admin_panel:client_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'active_page': 'clients',
            'title': 'Create Client',
            'subtitle': 'Add a new client',
        })
        return context
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Create user account
                username = self.request.POST.get('username')
                email = self.request.POST.get('email')
                password = self.request.POST.get('password1')
                
                if not username or not email or not password:
                    messages.error(self.request, 'Username, email, and password are required.')
                    return self.form_invalid(form)
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                )
                form.instance.user = user
                response = super().form_valid(form)
                messages.success(self.request, f'Client "{form.instance.company_name}" created successfully!')
                return response
        except Exception as e:
            messages.error(self.request, f'Error creating client: {str(e)}')
            return self.form_invalid(form)


class ClientDetailView(AdminRequiredMixin, DetailView):
    model = Client
    template_name = 'admin_panel/clients/detail.html'
    context_object_name = 'client'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'clients'
        context['projects'] = self.object.projects.all()[:10]
        context['tickets'] = self.object.tickets.all()[:10]
        context['invoices'] = self.object.invoices.all()[:10] if hasattr(self.object, 'invoices') else []
        return context


class ClientUpdateView(AdminRequiredMixin, UpdateView):
    model = Client
    fields = ['company_name', 'phone', 'address', 'town', 'county', 
              'tax_id', 'business_type']
    template_name = 'admin_panel/clients/create.html'
    success_url = reverse_lazy('admin_panel:client_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'active_page': 'clients',
            'title': 'Update Client',
            'subtitle': f'Editing "{self.object.company_name}"',
        })
        return context
    
    def form_valid(self, form):
        # Also update user email if provided
        email = self.request.POST.get('email')
        if email and self.object.user:
            self.object.user.email = email
            self.object.user.save()
        messages.success(self.request, f'Client "{form.instance.company_name}" updated successfully!')
        return super().form_valid(form)


class ClientDeleteView(AdminRequiredMixin, DeleteView):
    model = Client
    template_name = 'admin_panel/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:client_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'object_type': 'Client',
            'object_name': self.object.company_name,
            'cancel_url': reverse_lazy('admin_panel:client_list'),
            'active_page': 'clients',
        })
        return context
    
    def form_valid(self, form):
        obj = self.get_object()
        messages.success(self.request, f'Client "{obj.company_name}" deleted successfully!')
        return super().form_valid(form)


# ============================================================================
# PROJECTS
# ============================================================================

class ProjectListView(AdminRequiredMixin, ListView):
    model = ClientProject
    template_name = 'admin_panel/projects/list.html'
    context_object_name = 'projects'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ClientProject.objects.select_related('client').all()
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        priority = self.request.GET.get('priority')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(client__company_name__icontains=search)
            )
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'active_page': 'projects',
            'status_choices': ClientProject.STATUS_CHOICES,
            'priority_choices': ClientProject.PRIORITY_CHOICES,
        })
        return context


class ProjectCreateView(AdminRequiredMixin, CreateView):
    model = ClientProject
    fields = ['client', 'name', 'description', 'service', 'package', 
              'quote_amount', 'deposit', 'balance', 'payment_status',
              'status', 'priority', 'installation_address', 'timeline',
              'start_date', 'expected_completion']
    template_name = 'admin_panel/projects/create.html'
    success_url = reverse_lazy('admin_panel:project_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'clients': Client.objects.all(),
            'services': Service.objects.filter(published=True),
            'packages': Package.objects.filter(published=True),
            'active_page': 'projects',
            'title': 'Create Project',
            'subtitle': 'Add a new client project',
        })
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Project "{form.instance.name}" created successfully!')
        return super().form_valid(form)


class ProjectDetailView(AdminRequiredMixin, DetailView):
    model = ClientProject
    template_name = 'admin_panel/projects/detail.html'
    context_object_name = 'project'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'projects'
        context['tasks'] = self.object.tasks.all()
        context['updates'] = self.object.updates.all()[:10]
        return context


class ProjectUpdateView(AdminRequiredMixin, UpdateView):
    model = ClientProject
    fields = ['client', 'name', 'description', 'service', 'package', 
              'quote_amount', 'deposit', 'balance', 'payment_status',
              'status', 'priority', 'installation_address', 'timeline',
              'start_date', 'expected_completion', 'actual_completion']
    template_name = 'admin_panel/projects/create.html'
    success_url = reverse_lazy('admin_panel:project_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'clients': Client.objects.all(),
            'services': Service.objects.filter(published=True),
            'packages': Package.objects.filter(published=True),
            'active_page': 'projects',
            'title': 'Update Project',
            'subtitle': f'Editing "{self.object.name}"',
        })
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Project "{form.instance.name}" updated successfully!')
        return super().form_valid(form)


class ProjectDeleteView(AdminRequiredMixin, DeleteView):
    model = ClientProject
    template_name = 'admin_panel/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:project_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'object_type': 'Project',
            'object_name': self.object.name,
            'cancel_url': reverse_lazy('admin_panel:project_list'),
            'active_page': 'projects',
        })
        return context
    
    def form_valid(self, form):
        obj = self.get_object()
        messages.success(self.request, f'Project "{obj.name}" deleted successfully!')
        return super().form_valid(form)


class ProjectCompleteView(AdminRequiredMixin, View):
    """Mark a project as completed via POST"""
    
    def post(self, request, pk):
        project = get_object_or_404(ClientProject, pk=pk)
        project.status = 'completed'
        project.actual_completion = timezone.now().date()
        project.save()
        messages.success(request, f'Project "{project.name}" marked as completed!')
        return redirect('admin_panel:project_detail', pk=project.id)


# ============================================================================
# TICKETS
# ============================================================================

class TicketListView(AdminRequiredMixin, ListView):
    model = Ticket
    template_name = 'admin_panel/tickets/list.html'
    context_object_name = 'tickets'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Ticket.objects.select_related('client').all()
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        
        if search:
            queryset = queryset.filter(
                Q(subject__icontains=search) |
                Q(client__company_name__icontains=search)
            )
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'active_page': 'tickets',
            'status_choices': Ticket.STATUS_CHOICES,
        })
        return context


class TicketDetailView(AdminRequiredMixin, DetailView):
    model = Ticket
    template_name = 'admin_panel/tickets/detail.html'
    context_object_name = 'ticket'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'active_page': 'tickets',
            'responses': self.object.responses.all(),
        })
        return context


class TicketUpdateView(AdminRequiredMixin, UpdateView):
    model = Ticket
    fields = ['status', 'priority', 'assigned_to', 'category']
    template_name = 'admin_panel/tickets/update.html'
    success_url = reverse_lazy('admin_panel:ticket_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'active_page': 'tickets',
            'title': 'Update Ticket',
            'subtitle': f'Editing "{self.object.subject}"',
        })
        return context
    
    def form_valid(self, form):
        if form.instance.status == 'resolved' and not form.instance.resolved_date:
            form.instance.resolved_date = timezone.now()
        messages.success(self.request, f'Ticket "{form.instance.subject}" updated successfully!')
        return super().form_valid(form)


class TicketDeleteView(AdminRequiredMixin, DeleteView):
    model = Ticket
    template_name = 'admin_panel/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:ticket_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'object_type': 'Support Ticket',
            'object_name': self.object.subject,
            'cancel_url': reverse_lazy('admin_panel:ticket_list'),
            'active_page': 'tickets',
        })
        return context
    
    def form_valid(self, form):
        obj = self.get_object()
        messages.success(self.request, f'Ticket "{obj.subject}" deleted successfully!')
        return super().form_valid(form)


# ============================================================================
# TESTIMONIALS
# ============================================================================

class TestimonialListView(AdminRequiredMixin, ListView):
    model = Testimonial
    template_name = 'admin_panel/testimonials/list.html'
    context_object_name = 'testimonials'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Testimonial.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(author__icontains=search) | Q(company__icontains=search)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'testimonials'
        return context


class TestimonialCreateView(AdminRequiredMixin, CreateView):
    model = Testimonial
    fields = ['author', 'company', 'position', 'content', 'rating', 
              'image', 'featured', 'active', 'order']
    template_name = 'admin_panel/testimonials/create.html'
    success_url = reverse_lazy('admin_panel:testimonial_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'active_page': 'testimonials',
            'title': 'Create Testimonial',
            'subtitle': 'Add a new testimonial',
        })
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Testimonial created successfully!')
        return super().form_valid(form)


class TestimonialUpdateView(AdminRequiredMixin, UpdateView):
    model = Testimonial
    fields = ['author', 'company', 'position', 'content', 'rating', 
              'image', 'featured', 'active', 'order']
    template_name = 'admin_panel/testimonials/create.html'
    success_url = reverse_lazy('admin_panel:testimonial_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'active_page': 'testimonials',
            'title': 'Update Testimonial',
            'subtitle': f'Editing "{self.object.author}"',
        })
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Testimonial updated successfully!')
        return super().form_valid(form)


class TestimonialDeleteView(AdminRequiredMixin, DeleteView):
    model = Testimonial
    template_name = 'admin_panel/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:testimonial_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'object_type': 'Testimonial',
            'object_name': self.object.author,
            'cancel_url': reverse_lazy('admin_panel:testimonial_list'),
            'active_page': 'testimonials',
        })
        return context
    
    def form_valid(self, form):
        obj = self.get_object()
        messages.success(self.request, f'Testimonial by "{obj.author}" deleted successfully!')
        return super().form_valid(form)


# ============================================================================
# FAQS
# ============================================================================

class FAQListView(AdminRequiredMixin, ListView):
    model = FAQ
    template_name = 'admin_panel/faqs/list.html'
    context_object_name = 'faqs'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = FAQ.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(question__icontains=search) | Q(answer__icontains=search)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'faqs'
        return context


class FAQCreateView(AdminRequiredMixin, CreateView):
    model = FAQ
    fields = ['category', 'question', 'answer', 'order', 'active']
    template_name = 'admin_panel/faqs/create.html'
    success_url = reverse_lazy('admin_panel:faq_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'active_page': 'faqs',
            'title': 'Create FAQ',
            'subtitle': 'Add a new FAQ',
        })
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'FAQ created successfully!')
        return super().form_valid(form)


class FAQUpdateView(AdminRequiredMixin, UpdateView):
    model = FAQ
    fields = ['category', 'question', 'answer', 'order', 'active']
    template_name = 'admin_panel/faqs/create.html'
    success_url = reverse_lazy('admin_panel:faq_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'active_page': 'faqs',
            'title': 'Update FAQ',
            'subtitle': f'Editing "{self.object.question[:50]}"',
        })
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'FAQ updated successfully!')
        return super().form_valid(form)


class FAQDeleteView(AdminRequiredMixin, DeleteView):
    model = FAQ
    template_name = 'admin_panel/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:faq_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'object_type': 'FAQ',
            'object_name': self.object.question[:50],
            'cancel_url': reverse_lazy('admin_panel:faq_list'),
            'active_page': 'faqs',
        })
        return context
    
    def form_valid(self, form):
        obj = self.get_object()
        messages.success(self.request, f'FAQ "{obj.question[:50]}" deleted successfully!')
        return super().form_valid(form)


# ============================================================================
# QUOTE REQUESTS
# ============================================================================

class QuoteListView(AdminRequiredMixin, ListView):
    model = QuoteRequest
    template_name = 'admin_panel/quotes/list.html'
    context_object_name = 'quotes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = QuoteRequest.objects.all()
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        service = self.request.GET.get('service')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(company__icontains=search)
            )
        if status:
            queryset = queryset.filter(status=status)
        if service:
            queryset = queryset.filter(service_type=service)
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'active_page': 'quotes',
            'status_choices': QuoteRequest.STATUS_CHOICES,
            'service_choices': QuoteRequest.SERVICE_CHOICES,
        })
        return context


class QuoteDetailView(AdminRequiredMixin, DetailView):
    model = QuoteRequest
    template_name = 'admin_panel/quotes/detail.html'
    context_object_name = 'quote'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'quotes'
        return context


class QuoteUpdateView(AdminRequiredMixin, UpdateView):
    model = QuoteRequest
    fields = ['status', 'notes']
    template_name = 'admin_panel/quotes/update.html'
    success_url = reverse_lazy('admin_panel:quote_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'active_page': 'quotes',
            'title': 'Update Quote Request',
            'subtitle': f'From {self.object.name}',
        })
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Quote request updated successfully!')
        return super().form_valid(form)


class QuoteDeleteView(AdminRequiredMixin, DeleteView):
    model = QuoteRequest
    template_name = 'admin_panel/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:quote_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'object_type': 'Quote Request',
            'object_name': f'{self.object.name} - {self.object.get_service_type_display()}',
            'cancel_url': reverse_lazy('admin_panel:quote_list'),
            'active_page': 'quotes',
        })
        return context
    
    def form_valid(self, form):
        obj = self.get_object()
        messages.success(self.request, f'Quote request from "{obj.name}" deleted successfully!')
        return super().form_valid(form)


# ============================================================================
# CONTACT MESSAGES
# ============================================================================

class ContactListView(AdminRequiredMixin, ListView):
    model = ContactMessage
    template_name = 'admin_panel/contacts/list.html'
    context_object_name = 'messages'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ContactMessage.objects.all()
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        inquiry_type = self.request.GET.get('type')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(subject__icontains=search)
            )
        if status:
            queryset = queryset.filter(status=status)
        if inquiry_type:
            queryset = queryset.filter(inquiry_type=inquiry_type)
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'active_page': 'contacts',
            'status_choices': ContactMessage.STATUS_CHOICES,
            'inquiry_choices': ContactMessage.INQUIRY_TYPES,
        })
        return context


class ContactDetailView(AdminRequiredMixin, DetailView):
    model = ContactMessage
    template_name = 'admin_panel/contacts/detail.html'
    context_object_name = 'message'
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if self.object.status == 'new':
            self.object.status = 'read'
            self.object.save()
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'contacts'
        return context


class ContactDeleteView(AdminRequiredMixin, DeleteView):
    model = ContactMessage
    template_name = 'admin_panel/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:contact_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'object_type': 'Contact Message',
            'object_name': f'{self.object.name} - {self.object.subject}',
            'cancel_url': reverse_lazy('admin_panel:contact_list'),
            'active_page': 'contacts',
        })
        return context
    
    def form_valid(self, form):
        obj = self.get_object()
        messages.success(self.request, f'Message from "{obj.name}" deleted successfully!')
        return super().form_valid(form)


class ContactMarkRepliedView(AdminRequiredMixin, View):
    """Mark a contact message as replied via POST"""
    
    def post(self, request, pk):
        message = get_object_or_404(ContactMessage, pk=pk)
        message.status = 'replied'
        message.save()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        messages.success(request, 'Message marked as replied!')
        return redirect('admin_panel:contact_detail', pk=message.id)


# ============================================================================
# SUBSCRIBERS
# ============================================================================

class SubscriberListView(AdminRequiredMixin, ListView):
    model = NewsletterSubscriber
    template_name = 'admin_panel/subscribers/list.html'
    context_object_name = 'subscribers'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = NewsletterSubscriber.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(email__icontains=search)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'subscribers'
        return context


class SubscriberDeleteView(AdminRequiredMixin, DeleteView):
    model = NewsletterSubscriber
    template_name = 'admin_panel/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:subscriber_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'object_type': 'Subscriber',
            'object_name': self.object.email,
            'cancel_url': reverse_lazy('admin_panel:subscriber_list'),
            'active_page': 'subscribers',
        })
        return context
    
    def form_valid(self, form):
        obj = self.get_object()
        messages.success(self.request, f'Subscriber "{obj.email}" deleted successfully!')
        return super().form_valid(form)


class SubscriberExportView(AdminRequiredMixin, View):
    """Export all active subscribers to CSV"""
    
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="subscribers_{}.csv"'.format(
            timezone.now().strftime('%Y%m%d')
        )
        
        writer = csv.writer(response)
        writer.writerow(['Email', 'Status', 'Confirmed', 'Subscribed Date'])
        
        subscribers = NewsletterSubscriber.objects.all()
        for sub in subscribers:
            writer.writerow([
                sub.email,
                'Active' if sub.is_active else 'Inactive',
                'Yes' if sub.confirmed else 'No',
                sub.subscribed_date.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response


# ============================================================================
# TEAM
# ============================================================================

class TeamListView(AdminRequiredMixin, ListView):
    model = TeamMember
    template_name = 'admin_panel/team/list.html'
    context_object_name = 'members'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = TeamMember.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(position__icontains=search)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'team'
        return context


class TeamCreateView(AdminRequiredMixin, CreateView):
    model = TeamMember
    fields = ['name', 'position', 'bio', 'photo', 'social_links', 'order', 'active']
    template_name = 'admin_panel/team/create.html'
    success_url = reverse_lazy('admin_panel:team_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'active_page': 'team',
            'title': 'Add Team Member',
            'subtitle': 'Add a new team member',
        })
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Team member "{form.instance.name}" added successfully!')
        return super().form_valid(form)


class TeamUpdateView(AdminRequiredMixin, UpdateView):
    model = TeamMember
    fields = ['name', 'position', 'bio', 'photo', 'social_links', 'order', 'active']
    template_name = 'admin_panel/team/create.html'
    success_url = reverse_lazy('admin_panel:team_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'active_page': 'team',
            'title': 'Update Team Member',
            'subtitle': f'Editing "{self.object.name}"',
        })
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Team member "{form.instance.name}" updated successfully!')
        return super().form_valid(form)


class TeamDeleteView(AdminRequiredMixin, DeleteView):
    model = TeamMember
    template_name = 'admin_panel/confirm_delete.html'
    success_url = reverse_lazy('admin_panel:team_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'object_type': 'Team Member',
            'object_name': self.object.name,
            'cancel_url': reverse_lazy('admin_panel:team_list'),
            'active_page': 'team',
        })
        return context
    
    def form_valid(self, form):
        obj = self.get_object()
        messages.success(self.request, f'Team member "{obj.name}" deleted successfully!')
        return super().form_valid(form)
