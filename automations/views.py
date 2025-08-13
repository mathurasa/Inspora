from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def automation_list(request):
    """Display list of automations"""
    return render(request, 'automations/automation_list.html', {
        'title': 'Automations'
    })
