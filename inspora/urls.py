"""
URL configuration for Inspora project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import api_status_dashboard, public_landing_page, home_dashboard
from accounts.views import google_login, google_callback
from django.shortcuts import render

def test_date_picker(request):
    return render(request, 'test_date_picker.html')

def test_task_date_picker(request):
    return render(request, 'test_task_date_picker.html')

def test_footer(request):
    return render(request, 'test_footer.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Public Landing Page (accessible to everyone)
    path('', public_landing_page, name='public_landing'),
    
    # Home Dashboard (for authenticated users)
    path('home/', home_dashboard, name='home_dashboard'),
    
    # Google OAuth2 Authentication (at root level)
    path('google/login/', google_login, name='google_login'),
    path('google/callback/', google_callback, name='google_callback'),
    
    # Test pages for date picker and footer
    path('test-date-picker/', test_date_picker, name='test_date_picker'),
    path('test-task-date-picker/', test_task_date_picker, name='test_task_date_picker'),
    path('test-footer/', test_footer, name='test_footer'),
    
    # App URLs
    path('dashboard/', include('accounts.urls', namespace='accounts')),
    path('projects/', include('projects.urls')),
    path('tasks/', include('tasks.urls')),
    path('goals/', include('goals.urls')),
    path('portfolios/', include('portfolios.urls')),
    path('forms/', include('forms.urls')),
    path('automations/', include('automations.urls')),
    path('templates/', include('templates_app.urls')),
    path('solutions/', include('solutions_app.urls')),
    path('notifications/', include('notifications_app.urls')),
    path('integrations/', include('integrations.urls')),
    path('audit/', include('audit.urls')),
    
    # API endpoints (including JWT authentication)
    path('api/', include('inspora.api_urls')),
    
    # API Status Dashboard
    path('api-status/', api_status_dashboard, name='api_status_dashboard'),
    
    # Blog
    path('blog/', include('blog.urls')),
    
    # Admin System & Sales
    path('admin-system/', include('admin_system.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    

