from django.urls import path
from . import views

app_name = 'automations'

urlpatterns = [
    path('', views.automation_list, name='automation_list'),
]
