"""
Views for the main Inspora project.
"""
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import os

def api_status_dashboard(request):
    """API Status Dashboard for monitoring system health."""
    # Mock data for demonstration
    api_statuses = {
        'Database': {'status': 'healthy', 'response_time': '12ms'},
        'Redis Cache': {'status': 'healthy', 'response_time': '3ms'},
        'External APIs': {'status': 'healthy', 'response_time': '45ms'},
        'File Storage': {'status': 'healthy', 'response_time': '8ms'},
    }
    
    context = {
        'api_statuses': api_statuses,
        'system_uptime': '99.9%',
        'last_check': '2024-08-19 09:30:00 UTC'
    }
    return render(request, 'api_status_dashboard.html', context)

def public_landing_page(request):
    """Public landing page for non-authenticated users."""
    # Mock data for features and solutions
    features = [
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
    ]
    
    solutions = [
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
    ]
    
    testimonials = [
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
    
    context = {
        'features': features,
        'solutions': solutions,
        'testimonials': testimonials
    }
    return render(request, 'public_landing.html', context)

def home_dashboard(request):
    """User-friendly home dashboard for authenticated users."""
    # Mock data for demonstration - in production, this would come from your models
    context = {
        'user': request.user,
        'stats': {
            'active_tasks': 24,
            'active_projects': 8,
            'team_members': 12,
            'tasks_done_this_week': 18,
            'efficiency': 85
        },
        'recent_projects': [
            {
                'name': 'Website Redesign',
                'description': 'Redesigning the company website with modern UI/UX',
                'progress': 75,
                'status': 'On Track',
                'due_in': '5 days',
                'status_class': 'bg-success'
            },
            {
                'name': 'Mobile App Development',
                'description': 'Building a new mobile application for iOS and Android',
                'progress': 45,
                'status': 'At Risk',
                'due_in': '12 days',
                'status_class': 'bg-warning'
            }
        ],
        'recent_activities': [
            {
                'type': 'project',
                'title': 'New project created',
                'description': 'Website Redesign • 2 hours ago',
                'icon': 'fas fa-plus'
            },
            {
                'type': 'task',
                'title': 'Task completed',
                'description': 'Design homepage mockup • 4 hours ago',
                'icon': 'fas fa-check'
            },
            {
                'type': 'team',
                'title': 'Team member added',
                'description': 'Sarah Chen joined • 1 day ago',
                'icon': 'fas fa-user-plus'
            },
            {
                'type': 'notification',
                'title': 'Deadline reminder',
                'description': 'Project review due tomorrow • 1 day ago',
                'icon': 'fas fa-bell'
            }
        ]
    }
    return render(request, 'home_dashboard.html', context)

