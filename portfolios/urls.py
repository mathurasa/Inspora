from django.urls import path
from . import views

app_name = 'portfolios'

urlpatterns = [
    path('', views.portfolio_list, name='portfolio_list'),
]
