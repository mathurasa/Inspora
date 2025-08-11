"""
API URLs for projects app.
"""
from django.urls import path
from django.http import JsonResponse

def api_status(request):
    """Simple API status endpoint for testing."""
    return JsonResponse({
        'status': 'success',
        'message': 'Projects API is working!',
        'app': 'projects',
        'endpoints': {
            'projects': '/api/projects/projects/',
            'sections': '/api/projects/sections/',
            'members': '/api/projects/members/'
        }
    })

urlpatterns = [
    path('', api_status, name='api_status'),
    path('status/', api_status, name='api_status_detail'),
]
