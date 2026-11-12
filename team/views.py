from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import TeamMember, JobOpening, JobApplication

class TeamListView(ListView):
    model = TeamMember
    template_name = 'team/team_list.html'
    context_object_name = 'members'
    
    def get_queryset(self):
        return TeamMember.objects.filter(active=True)

class TeamMemberDetailView(DetailView):
    model = TeamMember
    template_name = 'team/team_member_detail.html'
    context_object_name = 'member'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

class JobApplicationCreateView(CreateView):
    model = JobApplication
    fields = ['full_name', 'email', 'phone', 'cover_letter', 'resume', 'portfolio_url', 'linkedin_url']
    template_name = 'team/job_apply.html'
    success_url = reverse_lazy('core:careers')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job'] = get_object_or_404(JobOpening, slug=self.kwargs.get('slug'), active=True)
        return context
    
    def form_valid(self, form):
        form.instance.job = get_object_or_404(JobOpening, slug=self.kwargs.get('slug'), active=True)
        messages.success(self.request, 'Your application has been submitted successfully!')
        return super().form_valid(form)
