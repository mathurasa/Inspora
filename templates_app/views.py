from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Template

@login_required
def template_list(request):
    """Display list of templates"""
    templates = Template.objects.all()
    return render(request, 'templates_app/template_list.html', {
        'templates': templates,
        'title': 'Templates'
    })

@login_required
def template_detail(request, pk):
    """Display template detail"""
    template = get_object_or_404(Template, pk=pk)
    return render(request, 'templates_app/template_detail.html', {
        'template': template,
        'title': template.name
    })
