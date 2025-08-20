"""
Views for admin_system app.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from datetime import datetime, timedelta
import json

from .models import (
    Company, CompanyMember, SalesLead, Invoice, 
    WorkflowTemplate, WorkflowInstance, AdminDashboard, SystemSettings
)
from .forms import (
    CompanyForm, CompanyMemberForm, SalesLeadForm, InvoiceForm,
    WorkflowTemplateForm, WorkflowInstanceForm, CompanySearchForm, SalesLeadSearchForm
)

User = get_user_model()


def is_admin_user(user):
    """Check if user is an admin user."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def is_company_admin(user, company):
    """Check if user is an admin for a specific company."""
    try:
        membership = CompanyMember.objects.get(user=user, company=company, is_active=True)
        return membership.role in ['owner', 'admin']
    except CompanyMember.DoesNotExist:
        return False


@login_required
@user_passes_test(is_admin_user)
def admin_dashboard(request):
    """Main admin dashboard view."""
    # Get key metrics
    total_companies = Company.objects.filter(is_active=True).count()
    total_leads = SalesLead.objects.count()
    total_revenue = Invoice.objects.filter(status='paid').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Get recent activities
    recent_companies = Company.objects.filter(is_active=True).order_by('-created_at')[:5]
    recent_leads = SalesLead.objects.order_by('-created_at')[:5]
    recent_invoices = Invoice.objects.order_by('-created_at')[:5]
    
    # Get conversion metrics
    conversion_data = Company.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Get monthly revenue
    current_month = timezone.now().month
    current_year = timezone.now().year
    monthly_revenue = Invoice.objects.filter(
        status='paid',
        paid_date__month=current_month,
        paid_date__year=current_year
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    context = {
        'total_companies': total_companies,
        'total_leads': total_leads,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'recent_companies': recent_companies,
        'recent_leads': recent_leads,
        'recent_invoices': recent_invoices,
        'conversion_data': conversion_data,
    }
    
    return render(request, 'admin_system/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin_user)
def company_list(request):
    """List all companies with search and filtering."""
    companies = Company.objects.all()
    
    # Handle search form
    search_form = CompanySearchForm(request.GET)
    if search_form.is_valid():
        search = search_form.cleaned_data.get('search')
        company_type = search_form.cleaned_data.get('company_type')
        status = search_form.cleaned_data.get('status')
        industry = search_form.cleaned_data.get('industry')
        
        if search:
            companies = companies.filter(
                Q(name__icontains=search) |
                Q(website__icontains=search) |
                Q(email__icontains=search) |
                Q(industry__icontains=search)
            )
        
        if company_type:
            companies = companies.filter(company_type=company_type)
        
        if status:
            companies = companies.filter(status=status)
        
        if industry:
            companies = companies.filter(industry__icontains=industry)
    
    # Pagination
    paginator = Paginator(companies, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_companies': companies.count(),
    }
    
    return render(request, 'admin_system/company_list.html', context)


@login_required
@user_passes_test(is_admin_user)
def company_detail(request, pk):
    """Detailed view of a company."""
    company = get_object_or_404(Company, pk=pk)
    members = CompanyMember.objects.filter(company=company, is_active=True)
    projects = company.projects.all() if hasattr(company, 'projects') else []
    invoices = company.invoices.all()
    
    context = {
        'company': company,
        'members': members,
        'projects': projects,
        'invoices': invoices,
    }
    
    return render(request, 'admin_system/company_detail.html', context)


@login_required
@user_passes_test(is_admin_user)
def company_create(request):
    """Create a new company."""
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.created_by = request.user
            company.save()
            messages.success(request, f'Company "{company.name}" created successfully.')
            return redirect('admin_system:company_detail', pk=company.pk)
    else:
        form = CompanyForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    
    return render(request, 'admin_system/company_form.html', context)


@login_required
@user_passes_test(is_admin_user)
def company_edit(request, pk):
    """Edit an existing company."""
    company = get_object_or_404(Company, pk=pk)
    
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, f'Company "{company.name}" updated successfully.')
            return redirect('admin_system:company_detail', pk=company.pk)
    else:
        form = CompanyForm(instance=company)
    
    context = {
        'form': form,
        'company': company,
        'action': 'Edit',
    }
    
    return render(request, 'admin_system/company_form.html', context)


@login_required
@user_passes_test(is_admin_user)
def company_member_add(request, company_pk):
    """Add a new member to a company."""
    company = get_object_or_404(Company, pk=company_pk)
    
    if request.method == 'POST':
        form = CompanyMemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.company = company
            member.save()
            messages.success(request, f'Member added to "{company.name}" successfully.')
            return redirect('admin_system:company_detail', pk=company.pk)
    else:
        form = CompanyMemberForm(initial={'company': company})
    
    context = {
        'form': form,
        'company': company,
    }
    
    return render(request, 'admin_system/company_member_form.html', context)


@login_required
@user_passes_test(is_admin_user)
def sales_lead_list(request):
    """List all sales leads with search and filtering."""
    leads = SalesLead.objects.all()
    
    # Handle search form
    search_form = SalesLeadSearchForm(request.GET)
    if search_form.is_valid():
        search = search_form.cleaned_data.get('search')
        lead_source = search_form.cleaned_data.get('lead_source')
        priority = search_form.cleaned_data.get('priority')
        status = search_form.cleaned_data.get('status')
        assigned_to = search_form.cleaned_data.get('assigned_to')
        
        if search:
            leads = leads.filter(
                Q(company_name__icontains=search) |
                Q(contact_person__icontains=search) |
                Q(email__icontains=search) |
                Q(notes__icontains=search)
            )
        
        if lead_source:
            leads = leads.filter(lead_source=lead_source)
        
        if priority:
            leads = leads.filter(priority=priority)
        
        if status:
            leads = leads.filter(status=status)
        
        if assigned_to:
            leads = leads.filter(assigned_to=assigned_to)
    
    # Pagination
    paginator = Paginator(leads, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_leads': leads.count(),
    }
    
    return render(request, 'admin_system/sales_lead_list.html', context)


@login_required
@user_passes_test(is_admin_user)
def sales_lead_detail(request, pk):
    """Detailed view of a sales lead."""
    lead = get_object_or_404(SalesLead, pk=pk)
    
    context = {
        'lead': lead,
    }
    
    return render(request, 'admin_system/sales_lead_detail.html', context)


@login_required
@user_passes_test(is_admin_user)
def sales_lead_create(request):
    """Create a new sales lead."""
    if request.method == 'POST':
        form = SalesLeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.created_by = request.user
            lead.save()
            messages.success(request, f'Sales lead for "{lead.company_name}" created successfully.')
            return redirect('admin_system:sales_lead_detail', pk=lead.pk)
    else:
        form = SalesLeadForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    
    return render(request, 'admin_system/sales_lead_form.html', context)


@login_required
@user_passes_test(is_admin_user)
def sales_lead_edit(request, pk):
    """Edit an existing sales lead."""
    lead = get_object_or_404(SalesLead, pk=pk)
    
    if request.method == 'POST':
        form = SalesLeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, f'Sales lead for "{lead.company_name}" updated successfully.')
            return redirect('admin_system:sales_lead_detail', pk=lead.pk)
    else:
        form = SalesLeadForm(instance=lead)
    
    context = {
        'form': form,
        'lead': lead,
        'action': 'Edit',
    }
    
    return render(request, 'admin_system/sales_lead_form.html', context)


@login_required
@user_passes_test(is_admin_user)
def invoice_list(request):
    """List all invoices."""
    invoices = Invoice.objects.all()
    
    # Pagination
    paginator = Paginator(invoices, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_invoices': invoices.count(),
        'total_revenue': invoices.filter(status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or 0,
    }
    
    return render(request, 'admin_system/invoice_list.html', context)


@login_required
@user_passes_test(is_admin_user)
def invoice_create(request):
    """Create a new invoice."""
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()
            messages.success(request, f'Invoice {invoice.invoice_number} created successfully.')
            return redirect('admin_system:invoice_list')
    else:
        form = InvoiceForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    
    return render(request, 'admin_system/invoice_form.html', context)


@login_required
@user_passes_test(is_admin_user)
def workflow_template_list(request):
    """List all workflow templates."""
    templates = WorkflowTemplate.objects.filter(is_active=True)
    
    # Pagination
    paginator = Paginator(templates, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_templates': templates.count(),
    }
    
    return render(request, 'admin_system/workflow_template_list.html', context)


@login_required
@user_passes_test(is_admin_user)
def workflow_template_create(request):
    """Create a new workflow template."""
    if request.method == 'POST':
        form = WorkflowTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.created_by = request.user
            template.save()
            messages.success(request, f'Workflow template "{template.name}" created successfully.')
            return redirect('admin_system:workflow_template_list')
    else:
        form = WorkflowTemplateForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    
    return render(request, 'admin_system/workflow_template_form.html', context)


@login_required
@user_passes_test(is_admin_user)
def workflow_instance_list(request):
    """List all workflow instances."""
    instances = WorkflowInstance.objects.all()
    
    # Pagination
    paginator = Paginator(instances, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_instances': instances.count(),
    }
    
    return render(request, 'admin_system/workflow_instance_list.html', context)


@login_required
@user_passes_test(is_admin_user)
def workflow_instance_create(request):
    """Create a new workflow instance."""
    if request.method == 'POST':
        form = WorkflowInstanceForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.owner = request.user
            instance.save()
            messages.success(request, f'Workflow instance "{instance.name}" created successfully.')
            return redirect('admin_system:workflow_instance_list')
    else:
        form = WorkflowInstanceForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    
    return render(request, 'admin_system/workflow_instance_form.html', context)


@login_required
@user_passes_test(is_admin_user)
def system_analytics(request):
    """System-wide analytics and reporting."""
    # Company metrics
    company_metrics = {
        'total_companies': Company.objects.filter(is_active=True).count(),
        'new_companies_this_month': Company.objects.filter(
            created_at__month=timezone.now().month,
            created_at__year=timezone.now().year
        ).count(),
        'companies_by_type': Company.objects.values('company_type').annotate(
            count=Count('id')
        ),
        'companies_by_status': Company.objects.values('status').annotate(
            count=Count('id')
        ),
    }
    
    # Sales metrics
    sales_metrics = {
        'total_leads': SalesLead.objects.count(),
        'leads_by_source': SalesLead.objects.values('lead_source').annotate(
            count=Count('id')
        ),
        'leads_by_priority': SalesLead.objects.values('priority').annotate(
            count=Count('id')
        ),
        'conversion_rate': Company.objects.filter(status='customer').count() / max(Company.objects.count(), 1) * 100,
    }
    
    # Revenue metrics
    revenue_metrics = {
        'total_revenue': Invoice.objects.filter(status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or 0,
        'monthly_revenue': Invoice.objects.filter(
            status='paid',
            paid_date__month=timezone.now().month,
            paid_date__year=timezone.now().year
        ).aggregate(total=Sum('total_amount'))['total'] or 0,
        'invoices_by_status': Invoice.objects.values('status').annotate(
            count=Count('id')
        ),
    }
    
    # Workflow metrics
    workflow_metrics = {
        'total_templates': WorkflowTemplate.objects.filter(is_active=True).count(),
        'total_instances': WorkflowInstance.objects.count(),
        'instances_by_status': WorkflowInstance.objects.values('status').annotate(
            count=Count('id')
        ),
    }
    
    context = {
        'company_metrics': company_metrics,
        'sales_metrics': sales_metrics,
        'revenue_metrics': revenue_metrics,
        'workflow_metrics': workflow_metrics,
    }
    
    return render(request, 'admin_system/system_analytics.html', context)


@login_required
@user_passes_test(is_admin_user)
def system_settings(request):
    """System settings management."""
    if request.method == 'POST':
        # Handle setting updates
        for key, value in request.POST.items():
            if key.startswith('setting_'):
                setting_key = key.replace('setting_', '')
                try:
                    setting = SystemSettings.objects.get(key=setting_key)
                    setting.value = value
                    setting.updated_by = request.user
                    setting.save()
                except SystemSettings.DoesNotExist:
                    SystemSettings.objects.create(
                        key=setting_key,
                        value=value,
                        updated_by=request.user
                    )
        
        messages.success(request, 'System settings updated successfully.')
        return redirect('admin_system:system_settings')
    
    # Get current settings
    settings = SystemSettings.objects.all()
    
    context = {
        'settings': settings,
    }
    
    return render(request, 'admin_system/system_settings.html', context)


# API Views for AJAX requests
@login_required
@user_passes_test(is_admin_user)
@require_http_methods(["POST"])
@csrf_exempt
def update_lead_status(request):
    """Update sales lead status via AJAX."""
    try:
        data = json.loads(request.body)
        lead_id = data.get('lead_id')
        new_status = data.get('status')
        
        lead = get_object_or_404(SalesLead, pk=lead_id)
        lead.status = new_status
        lead.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Lead status updated to {new_status}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@user_passes_test(is_admin_user)
@require_http_methods(["POST"])
@csrf_exempt
def update_invoice_status(request):
    """Update invoice status via AJAX."""
    try:
        data = json.loads(request.body)
        invoice_id = data.get('invoice_id')
        new_status = data.get('status')
        
        invoice = get_object_or_404(Invoice, pk=invoice_id)
        invoice.status = new_status
        
        if new_status == 'paid':
            invoice.paid_date = timezone.now().date()
        
        invoice.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Invoice status updated to {new_status}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
