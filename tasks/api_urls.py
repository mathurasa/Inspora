"""
API URLs for tasks app.
"""
from django.urls import path
from django.http import JsonResponse

def api_status(request):
    """Simple API status endpoint for testing."""
    return JsonResponse({
        'status': 'success',
        'message': 'Tasks API is working!',
        'app': 'tasks',
        'endpoints': {
            'tasks': '/api/tasks/tasks/',
            'comments': '/api/tasks/comments/',
            'attachments': '/api/tasks/attachments/'
        }
    })

urlpatterns = [
    path('', api_status, name='api_status'),
    path('status/', api_status, name='api_status_detail'),
]
