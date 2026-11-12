from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Ticket, TicketResponse, KnowledgeBase
from clients.models import Client

class TicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'support/ticket_list.html'
    context_object_name = 'tickets'
    paginate_by = 10
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Ticket.objects.all()
        try:
            client = Client.objects.get(user=self.request.user)
            return Ticket.objects.filter(client=client)
        except Client.DoesNotExist:
            return Ticket.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_counts'] = {
            'all': self.get_queryset().count(),
            'open': self.get_queryset().filter(status='open').count(),
            'in_progress': self.get_queryset().filter(status='in_progress').count(),
            'resolved': self.get_queryset().filter(status='resolved').count(),
        }
        return context

class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'support/ticket_detail.html'
    context_object_name = 'ticket'
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Ticket.objects.all()
        try:
            client = Client.objects.get(user=self.request.user)
            return Ticket.objects.filter(client=client)
        except Client.DoesNotExist:
            return Ticket.objects.none()

class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    fields = ['subject', 'description', 'category', 'priority', 'project']
    template_name = 'support/ticket_create.html'
    success_url = reverse_lazy('support:tickets')
    
    def get_form(self):
        form = super().get_form()
        try:
            client = Client.objects.get(user=self.request.user)
            form.fields['project'].queryset = client.projects.all()
        except Client.DoesNotExist:
            pass
        return form
    
    def form_valid(self, form):
        try:
            client = Client.objects.get(user=self.request.user)
            form.instance.client = client
        except Client.DoesNotExist:
            messages.error(self.request, 'Please complete your client profile first.')
            return redirect('clients:profile')
        messages.success(self.request, 'Ticket created successfully!')
        return super().form_valid(form)

class TicketResponseCreateView(LoginRequiredMixin, CreateView):
    model = TicketResponse
    fields = ['message', 'attachment']
    template_name = 'support/ticket_response.html'
    
    def form_valid(self, form):
        ticket = get_object_or_404(Ticket, id=self.kwargs.get('ticket_id'))
        form.instance.ticket = ticket
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Response added successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('support:ticket_detail', kwargs={'pk': self.kwargs.get('ticket_id')})

@login_required
def ticket_resolve_view(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.user.is_staff or ticket.client.user == request.user:
        if request.method == 'POST':
            ticket.resolve()
            messages.success(request, 'Ticket marked as resolved!')
            return redirect('support:ticket_detail', pk=ticket.id)
    return render(request, 'support/ticket_resolve_confirm.html', {'ticket': ticket})

class KnowledgeBaseView(ListView):
    model = KnowledgeBase
    template_name = 'support/knowledge_base.html'
    context_object_name = 'articles'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = KnowledgeBase.objects.all()
        category = self.request.GET.get('category')
        search = self.request.GET.get('search')
        if category:
            queryset = queryset.filter(category=category)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(tags__icontains=search)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = KnowledgeBase.CATEGORY_CHOICES
        return context

class KnowledgeBaseDetailView(DetailView):
    model = KnowledgeBase
    template_name = 'support/knowledge_base_detail.html'
    context_object_name = 'article'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.object.views_count += 1
        self.object.save(update_fields=['views_count'])
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_articles'] = KnowledgeBase.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id)[:5]
        return context

@login_required
def kb_helpful_view(request, slug):
    article = get_object_or_404(KnowledgeBase, slug=slug)
    if request.method == 'POST':
        helpful = request.POST.get('helpful') == 'true'
        if helpful:
            article.helpful_count += 1
        else:
            article.not_helpful_count += 1
        article.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
