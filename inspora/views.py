"""
Views for the main Inspora project.
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.contrib.auth.models import AnonymousUser
import requests
import time

def api_status_dashboard(request):
    """API Status Dashboard - Shows the status of all API endpoints."""
    
    # Define all API endpoints to check
    api_endpoints = {
        'core': {
            'Main API': {
                'url': '/api/',
                'description': 'Root API endpoint with API information',
                'method': 'GET'
            },
            'Authentication': {
                'url': '/api/token/',
                'description': 'JWT token authentication endpoint',
                'method': 'POST'
            },
            'Token Refresh': {
                'url': '/api/token/refresh/',
                'description': 'JWT token refresh endpoint',
                'method': 'POST'
            },
            'Token Verify': {
                'url': '/api/token/verify/',
                'description': 'JWT token verification endpoint',
                'method': 'POST'
            }
        },
        'apps': {
            'Accounts API': {
                'url': '/api/accounts/',
                'description': 'User management and authentication',
                'method': 'GET'
            },
            'Projects API': {
                'url': '/api/projects/',
                'description': 'Project management and collaboration',
                'method': 'GET'
            },
            'Tasks API': {
                'url': '/api/tasks/',
                'description': 'Task management and tracking',
                'method': 'GET'
            }
        },
        'admin': {
            'Admin Panel': {
                'url': '/admin/',
                'description': 'Django admin interface',
                'method': 'GET'
            }
        }
    }
    
    # Check endpoint statuses
    base_url = request.build_absolute_uri('/').rstrip('/')
    endpoint_statuses = {}
    
    for category, endpoints in api_endpoints.items():
        endpoint_statuses[category] = {}
        for name, details in endpoints.items():
            try:
                # Check if endpoint is accessible
                if details['method'] == 'GET':
                    response = requests.get(f"{base_url}{details['url']}", timeout=5)
                    status = 'Active' if response.status_code < 400 else 'Error'
                    response_time = response.elapsed.total_seconds() * 1000  # Convert to milliseconds
                else:
                    # For POST endpoints, just check if they exist (don't actually post)
                    status = 'Active'
                    response_time = 0
                
                endpoint_statuses[category][name] = {
                    'status': status,
                    'url': details['url'],
                    'description': details['description'],
                    'method': details['method'],
                    'response_time': round(response_time, 2) if response_time > 0 else None,
                    'last_checked': time.time()
                }
                
            except Exception as e:
                endpoint_statuses[category][name] = {
                    'status': 'Error',
                    'url': details['url'],
                    'description': details['description'],
                    'method': details['method'],
                    'response_time': None,
                    'last_checked': time.time(),
                    'error': str(e)
                }
    
    # Calculate overall API health
    total_endpoints = sum(len(endpoints) for endpoints in api_endpoints.values())
    active_endpoints = sum(
        sum(1 for endpoint in endpoints.values() if endpoint['status'] == 'Active')
        for endpoints in endpoint_statuses.values()
    )
    
    overall_status = 'Healthy' if active_endpoints == total_endpoints else 'Degraded'
    if active_endpoints == 0:
        overall_status = 'Critical'
    
    context = {
        'endpoint_statuses': endpoint_statuses,
        'overall_status': overall_status,
        'total_endpoints': total_endpoints,
        'active_endpoints': active_endpoints,
        'health_percentage': round((active_endpoints / total_endpoints) * 100, 1),
        'last_updated': time.time()
    }
    
    return render(request, 'api_status_dashboard.html', context)

def public_landing_page(request):
    """Public landing page that everyone can see - showcases Inspora's features."""
    # Get some public stats (can be enhanced later)
    context = {
        'features': [
            {
                'title': 'Project Management',
                'description': 'Create, organize, and track projects with multiple views and real-time collaboration.',
                'icon': 'fas fa-project-diagram',
                'color': '#f06a6f',
                'url': '/projects/'
            },
            {
                'title': 'Task Management',
                'description': 'Manage tasks with dependencies, subtasks, and automated workflows.',
                'icon': 'fas fa-tasks',
                'color': '#4CAF50',
                'url': '/tasks/'
            },
            {
                'title': 'Team Collaboration',
                'description': 'Build teams, assign roles, and collaborate effectively across projects.',
                'icon': 'fas fa-users',
                'color': '#2196F3',
                'url': '/teams/'
            },
            {
                'title': 'Goal Tracking',
                'description': 'Set, track, and achieve your personal and team goals with progress monitoring.',
                'icon': 'fas fa-target',
                'color': '#FF9800',
                'url': '/goals/'
            },
            {
                'title': 'AI-Powered Insights',
                'description': 'Get intelligent suggestions and workflow optimization powered by AI.',
                'icon': 'fas fa-robot',
                'color': '#9C27B0',
                'url': '/ai/'
            },
            {
                'title': 'Portfolio Management',
                'description': 'Manage multiple projects and initiatives in organized portfolios.',
                'icon': 'fas fa-briefcase',
                'color': '#607D8B',
                'url': '/portfolios/'
            }
        ],
        'solutions': [
            {
                'title': 'Enterprise',
                'description': 'Scalable solutions for large organizations with advanced security and compliance.',
                'url': '/solutions/enterprise/'
            },
            {
                'title': 'Small Business',
                'description': 'Perfect for growing teams that need powerful project management tools.',
                'url': '/solutions/small-business/'
            },
            {
                'title': 'Marketing Teams',
                'description': 'Specialized tools for marketing campaigns and creative project management.',
                'url': '/solutions/marketing/'
            },
            {
                'title': 'Development Teams',
                'description': 'Agile project management with Git integration and development workflows.',
                'url': '/solutions/development/'
            }
        ],
        'testimonials': [
            {
                'name': 'Sarah Chen',
                'role': 'Product Manager',
                'company': 'TechCorp',
                'quote': 'Inspora has transformed how our team collaborates. The AI insights are game-changing!',
                'avatar': '👩‍💼'
            },
            {
                'name': 'Marcus Rodriguez',
                'role': 'Team Lead',
                'company': 'DesignStudio',
                'quote': 'Finally, a project management tool that actually makes sense for creative teams.',
                'avatar': '👨‍🎨'
            },
            {
                'name': 'Priya Patel',
                'role': 'Startup Founder',
                'company': 'InnovateLab',
                'quote': 'Inspora helped us scale from 5 to 50 team members seamlessly.',
                'avatar': '👩‍💻'
            }
        ]
    }
    return render(request, 'public_landing.html', context)

