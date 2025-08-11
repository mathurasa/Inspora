"""
API URLs for accounts app.
"""
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def api_status(request):
    """Simple API status endpoint for testing."""
    return JsonResponse({
        'status': 'success',
        'message': 'Inspora API is working!',
        'app': 'accounts',
        'endpoints': {
            'users': '/api/accounts/users/',
            'teams': '/api/accounts/teams/',
            'profile': '/api/accounts/profile/'
        }
    })

urlpatterns = [
    path('', api_status, name='api_status'),
    path('status/', api_status, name='api_status_detail'),
]
