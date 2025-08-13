"""
URL configuration for Inspora project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import google_login, google_callback

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Google OAuth2 Authentication (at root level)
    path('google/login/', google_login, name='google_login'),
    path('google/callback/', google_callback, name='google_callback'),
    
    # API endpoints (including JWT authentication)
    path('api/', include('inspora.api_urls')),
    
    # App URLs
    path('', include('accounts.urls')),
    path('projects/', include('projects.urls')),
    path('tasks/', include('tasks.urls')),
    path('goals/', include('goals.urls')),
    path('forms/', include('forms.urls')),
    path('audit/', include('audit.urls')),
    path('automations/', include('automations.urls')),
    path('portfolios/', include('portfolios.urls')),
    path('notifications/', include('notifications_app.urls')),
    path('templates/', include('templates_app.urls')),
    path('solutions/', include('solutions_app.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    

