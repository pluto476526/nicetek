from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Project, Task, ProjectUpdate
from clients.models import Client
from services.models import Service
from packages.models import Package

class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Project.objects.all()
        if self.request.user.is_staff:
            # Admin sees all
            return queryset
        else:
            # Client sees their own
            try:
                client = Client.objects.get(user=self.request.user)
                return queryset.filter(client=client)
            except Client.DoesNotExist:
                return Project.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_counts'] = {
            'all': self.get_queryset().count(),
            'planning': self.get_queryset().filter(status='planning').count(),
            'in_progress': self.get_queryset().filter(status='in_progress').count(),
            'completed': self.get_queryset().filter(status='completed').count(),
        }
        return context

class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Project.objects.all()
        else:
            try:
                client = Client.objects.get(user=self.request.user)
                return Project.objects.filter(client=client)
            except Client.DoesNotExist:
                return Project.objects.none()

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    fields = ['name', 'description', 'service', 'package', 'installation_address', 'timeline']
    template_name = 'projects/project_create.html'
    success_url = reverse_lazy('projects:list')
    
    def get_form(self):
        form = super().get_form()
        # Filter services and packages
        form.fields['service'].queryset = Service.objects.filter(published=True)
        form.fields['package'].queryset = Package.objects.filter(published=True)
        return form
    
    def form_valid(self, form):
        try:
            client = Client.objects.get(user=self.request.user)
            form.instance.client = client
        except Client.DoesNotExist:
            messages.error(self.request, 'Please complete your client profile first.')
            return redirect('clients:profile')
        
        messages.success(self.request, 'Project created successfully!')
        return super().form_valid(form)

class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    fields = ['name', 'description', 'status', 'priority', 'timeline', 'start_date', 'expected_completion']
    template_name = 'projects/project_update.html'
    success_url = reverse_lazy('projects:list')
    
    def test_func(self):
        project = self.get_object()
        if self.request.user.is_staff:
            return True
        try:
            client = Client.objects.get(user=self.request.user)
            return project.client == client
        except Client.DoesNotExist:
            return False
    
    def form_valid(self, form):
        messages.success(self.request, 'Project updated successfully!')
        return super().form_valid(form)

class TaskCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Task
    fields = ['name', 'description', 'assigned_to', 'priority', 'due_date']
    template_name = 'projects/task_create.html'
    
    def test_func(self):
        project = get_object_or_404(Project, id=self.kwargs.get('project_id'))
        if self.request.user.is_staff:
            return True
        try:
            client = Client.objects.get(user=self.request.user)
            return project.client == client
        except Client.DoesNotExist:
            return False
    
    def form_valid(self, form):
        form.instance.project = get_object_or_404(Project, id=self.kwargs.get('project_id'))
        messages.success(self.request, 'Task created successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.kwargs.get('project_id')})

class ProjectStatusUpdateView(LoginRequiredMixin, CreateView):
    model = ProjectUpdate
    fields = ['update_text', 'attached_files']
    template_name = 'projects/status_update.html'
    
    def form_valid(self, form):
        form.instance.project = get_object_or_404(Project, id=self.kwargs.get('project_id'))
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Status update added successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.kwargs.get('project_id')})

@login_required
def project_complete_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.status = 'completed'
        project.actual_completion = timezone.now().date()
        project.save()
        messages.success(request, 'Project marked as completed!')
        return redirect('projects:detail', pk=project.id)
    return render(request, 'projects/project_complete_confirm.html', {'project': project})
