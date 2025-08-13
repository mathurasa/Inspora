from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def audit_list(request):
    """Display list of audit records"""
    return render(request, 'audit/audit_list.html', {
        'title': 'Audit Log'
    })
