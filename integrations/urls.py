from django.urls import path
from . import views

app_name = 'integrations'

urlpatterns = [
    # Integration Hub
    path('', views.integration_hub, name='integration_hub'),
    
    # Google Drive Integration
    path('google-drive/connect/', views.google_drive_connect, name='google_drive_connect'),
    path('google-drive/callback/', views.google_drive_callback, name='google_drive_callback'),
    path('google-drive/disconnect/', views.google_drive_disconnect, name='google_drive_disconnect'),
    path('google-drive/files/', views.google_drive_files, name='google_drive_files'),
    path('google-drive/upload/', views.google_drive_upload, name='google_drive_upload'),
    
    # Integration Management
    path('<int:integration_id>/logs/', views.integration_logs, name='integration_logs'),
    path('<int:integration_id>/test/', views.test_integration, name='test_integration'),
    path('<int:integration_id>/delete/', views.delete_integration, name='delete_integration'),
]






