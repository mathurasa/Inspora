"""
API URL configuration for Inspora project.
"""
from django.urls import path, include
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

def api_root(request):
    """Root API endpoint."""
    return JsonResponse({
        'status': 'success',
        'message': 'Welcome to Inspora API!',
        'version': '1.0.0',
        'endpoints': {
            'authentication': {
                'token': '/api/token/',
                'token_refresh': '/api/token/refresh/',
                'token_verify': '/api/token/verify/'
            },
            'apps': {
                'accounts': '/api/accounts/',
                'projects': '/api/projects/',
                'tasks': '/api/tasks/'
            }
        }
    })

urlpatterns = [
    # Root API endpoint
    path('', api_root, name='api_root'),
    
    # JWT authentication
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API endpoints for each app
    path('accounts/', include('accounts.api_urls')),
    path('projects/', include('projects.api_urls')),
    path('tasks/', include('tasks.api_urls')),
]
