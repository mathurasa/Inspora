from django.urls import path
from . import views

app_name = 'notifications_app'

urlpatterns = [
    # Main notification views
    path('', views.notification_list, name='notification_list'),
    path('<int:pk>/', views.notification_detail, name='notification_detail'),
    path('preferences/', views.notification_preferences, name='preferences'),
    
    # API endpoints for AJAX requests
    path('api/unread/', views.api_unread_notifications, name='api_unread'),
    path('api/<int:notification_id>/read/', views.api_mark_notification_read, name='api_mark_read'),
    path('api/mark-all-read/', views.api_mark_all_read, name='api_mark_all_read'),
    path('api/stats/', views.api_notification_stats, name='api_stats'),
    path('api/test/', views.api_test_notification, name='api_test'),
    path('api/<int:notification_id>/delete/', views.api_delete_notification, name='api_delete'),
    path('api/<int:notification_id>/archive/', views.api_archive_notification, name='api_archive'),
    path('api/preferences/', views.api_notification_preferences, name='api_preferences'),
    path('api/preferences/update/', views.api_update_preferences, name='api_update_preferences'),
]

