from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def form_list(request):
    """Display list of forms"""
    return render(request, 'forms/form_list.html', {
        'title': 'Forms'
    })
