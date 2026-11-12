from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from .models import BlogPost, PostCategory, Comment
from .forms import CommentForm

class BlogListView(ListView):
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = BlogPost.objects.filter(published=True)
        category = self.request.GET.get('category')
        tag = self.request.GET.get('tag')
        search = self.request.GET.get('search')
        
        if category:
            queryset = queryset.filter(category__slug=category)
        if tag:
            queryset = queryset.filter(tags__contains=[tag])
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(excerpt__icontains=search) |
                Q(content__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = PostCategory.objects.all()
        context['featured_posts'] = BlogPost.objects.filter(published=True, featured=True)[:3]
        # Get all unique tags
        tags = []
        for post in BlogPost.objects.filter(published=True):
            tags.extend(post.tags)
        context['tags'] = list(set(tags))[:10]
        return context

class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return BlogPost.objects.filter(published=True)
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.object.views_count += 1
        self.object.save(update_fields=['views_count'])
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_posts'] = BlogPost.objects.filter(
            category=self.object.category,
            published=True
        ).exclude(id=self.object.id)[:3]
        context['comments'] = Comment.objects.filter(post=self.object, approved=True, parent=None)
        context['comment_form'] = CommentForm()
        return context

class BlogCategoryView(ListView):
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        self.category = get_object_or_404(PostCategory, slug=self.kwargs.get('slug'))
        return BlogPost.objects.filter(category=self.category, published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = PostCategory.objects.all()
        context['current_category'] = self.category
        return context

class BlogTagView(ListView):
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        self.tag = self.kwargs.get('tag')
        return BlogPost.objects.filter(tags__contains=[self.tag], published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_tag'] = self.tag
        context['categories'] = PostCategory.objects.all()
        return context

class BlogSearchView(ListView):
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return BlogPost.objects.filter(
                Q(title__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(content__icontains=query),
                published=True
            )
        return BlogPost.objects.filter(published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = PostCategory.objects.all()
        context['search_query'] = self.request.GET.get('q', '')
        return context

class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentForm
    http_method_names = ['post']
    
    def form_valid(self, form):
        post = get_object_or_404(BlogPost, slug=self.kwargs.get('slug'), published=True)
        form.instance.post = post
        if 'parent_id' in self.request.POST:
            parent = get_object_or_404(Comment, id=self.request.POST.get('parent_id'))
            form.instance.parent = parent
        messages.success(self.request, 'Your comment has been submitted and is awaiting approval.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('blog:detail', kwargs={'slug': self.kwargs.get('slug')})
