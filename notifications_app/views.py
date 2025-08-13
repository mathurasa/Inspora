from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def notification_list(request):
    """Display list of notifications"""
    return render(request, 'notifications_app/notification_list.html', {
        'title': 'Notifications'
    })
