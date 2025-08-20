"""
URL patterns for admin_system app.
"""
from django.urls import path
from . import views

app_name = 'admin_system'

urlpatterns = [
    # Admin Dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Company Management
    path('companies/', views.company_list, name='company_list'),
    path('companies/create/', views.company_create, name='company_create'),
    path('companies/<int:pk>/', views.company_detail, name='company_detail'),
    path('companies/<int:pk>/edit/', views.company_edit, name='company_edit'),
    path('companies/<int:company_pk>/members/add/', views.company_member_add, name='company_member_add'),
    
    # Sales Lead Management
    path('leads/', views.sales_lead_list, name='sales_lead_list'),
    path('leads/create/', views.sales_lead_create, name='sales_lead_create'),
    path('leads/<int:pk>/', views.sales_lead_detail, name='sales_lead_detail'),
    path('leads/<int:pk>/edit/', views.sales_lead_edit, name='sales_lead_edit'),
    
    # Invoice Management
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    
    # Workflow Management
    path('workflows/templates/', views.workflow_template_list, name='workflow_template_list'),
    path('workflows/templates/create/', views.workflow_template_create, name='workflow_template_create'),
    path('workflows/instances/', views.workflow_instance_list, name='workflow_instance_list'),
    path('workflows/instances/create/', views.workflow_instance_create, name='workflow_instance_create'),
    
    # System Management
    path('analytics/', views.system_analytics, name='system_analytics'),
    path('settings/', views.system_settings, name='system_settings'),
    
    # API Endpoints
    path('api/leads/update-status/', views.update_lead_status, name='update_lead_status'),
    path('api/invoices/update-status/', views.update_invoice_status, name='update_invoice_status'),
]
