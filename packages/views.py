from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q
from .models import Package, PackageCategory, PackageComparison

class PackageListView(ListView):
    model = Package
    template_name = 'packages/package_list.html'
    context_object_name = 'packages'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Package.objects.filter(published=True)
        category = self.request.GET.get('category')
        search = self.request.GET.get('search')
        sort = self.request.GET.get('sort')
        
        if category:
            queryset = queryset.filter(category__slug=category)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'featured':
            queryset = queryset.filter(is_featured=True)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = PackageCategory.objects.all()
        return context

class PackageDetailView(DetailView):
    model = Package
    template_name = 'packages/package_detail.html'
    context_object_name = 'package'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_packages'] = Package.objects.filter(
            category=self.object.category,
            published=True
        ).exclude(id=self.object.id)[:3]
        return context

class PackageCategoryView(ListView):
    model = Package
    template_name = 'packages/package_list.html'
    context_object_name = 'packages'
    paginate_by = 9
    
    def get_queryset(self):
        self.category = get_object_or_404(PackageCategory, slug=self.kwargs.get('slug'))
        return Package.objects.filter(category=self.category, published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = PackageCategory.objects.all()
        context['current_category'] = self.category
        return context

class PackageCompareView(TemplateView):
    template_name = 'packages/package_compare.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        package_ids = self.request.GET.getlist('ids')
        context['packages'] = Package.objects.filter(id__in=package_ids, published=True)
        context['all_packages'] = Package.objects.filter(published=True)
        return context
