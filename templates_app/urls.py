from django.urls import path
from . import views

app_name = 'templates'

urlpatterns = [
    path('', views.template_list, name='template_list'),
    path('<int:pk>/', views.template_detail, name='template_detail'),
]
