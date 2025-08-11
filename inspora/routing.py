"""
WebSocket routing configuration for Inspora project.
"""
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),
    path('ws/projects/<int:project_id>/', consumers.ProjectConsumer.as_asgi()),
    path('ws/tasks/<int:task_id>/', consumers.TaskConsumer.as_asgi()),
]
