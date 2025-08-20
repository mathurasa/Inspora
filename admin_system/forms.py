"""
Forms for admin_system app.
"""
from django import forms
from django.contrib.auth import get_user_model
from .models import (
    Company, CompanyMember, SalesLead, Invoice, 
    WorkflowTemplate, WorkflowInstance
)

User = get_user_model()


class CompanyForm(forms.ModelForm):
    """Form for creating and editing companies."""
    
    class Meta:
        model = Company
        fields = [
            'name', 'company_type', 'status', 'website', 'phone', 'email',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
            'industry', 'company_size', 'annual_revenue', 'founded_year',
            'lead_source', 'sales_rep', 'conversion_date',
            'subscription_plan', 'subscription_start', 'subscription_end', 'monthly_recurring_revenue',
            'is_active', 'allow_guest_access', 'max_users', 'max_projects'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'company_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contact@company.com'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street Address'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Suite, Apt, etc.'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State/Province'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ZIP/Postal Code'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'industry': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Industry'}),
            'company_size': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of employees'}),
            'annual_revenue': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'founded_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Year founded'}),
            'lead_source': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'How did you find us?'}),
            'sales_rep': forms.Select(attrs={'class': 'form-select'}),
            'conversion_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'subscription_plan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Plan name'}),
            'subscription_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'subscription_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'monthly_recurring_revenue': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'max_users': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_projects': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter sales reps to only admin users
        self.fields['sales_rep'].queryset = User.objects.filter(is_staff=True)
        
        # Add Bootstrap classes to checkboxes
        self.fields['is_active'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['allow_guest_access'].widget.attrs.update({'class': 'form-check-input'})


class CompanyMemberForm(forms.ModelForm):
    """Form for adding/editing company members."""
    
    class Meta:
        model = CompanyMember
        fields = [
            'user', 'company', 'role', 'is_active',
            'can_manage_company', 'can_manage_users', 'can_manage_projects',
            'can_manage_billing', 'can_view_analytics', 'can_export_data'
        ]
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_company': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_users': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_projects': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_billing': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_view_analytics': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_export_data': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SalesLeadForm(forms.ModelForm):
    """Form for creating and editing sales leads."""
    
    class Meta:
        model = SalesLead
        fields = [
            'company_name', 'contact_person', 'email', 'phone',
            'lead_source', 'priority', 'estimated_value', 'status', 'notes',
            'assigned_to', 'next_follow_up'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Person Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contact@company.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'}),
            'lead_source': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'estimated_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Additional notes about this lead...'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'next_follow_up': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter assigned_to to only admin users
        self.fields['assigned_to'].queryset = User.objects.filter(is_staff=True)


class InvoiceForm(forms.ModelForm):
    """Form for creating and editing invoices."""
    
    class Meta:
        model = Invoice
        fields = [
            'invoice_number', 'company', 'amount', 'tax_amount',
            'issue_date', 'due_date', 'status', 'notes'
        ]
        widgets = {
            'invoice_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'INV-001'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'tax_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Invoice notes...'}),
        }


class WorkflowTemplateForm(forms.ModelForm):
    """Form for creating and editing workflow templates."""
    
    class Meta:
        model = WorkflowTemplate
        fields = [
            'name', 'description', 'workflow_type', 'is_public', 'is_featured', 
            'is_active', 'estimated_duration', 'company'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Workflow Template Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe this workflow template...'}),
            'workflow_type': forms.Select(attrs={'class': 'form-select'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'estimated_duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Days'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
        }


class WorkflowInstanceForm(forms.ModelForm):
    """Form for creating and editing workflow instances."""
    
    class Meta:
        model = WorkflowInstance
        fields = [
            'name', 'workflow_template', 'company', 'status', 'progress',
            'start_date', 'target_date', 'owner', 'assigned_team'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Workflow Instance Name'}),
            'workflow_template': forms.Select(attrs={'class': 'form-select'}),
            'company': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'progress': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'target_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'owner': forms.Select(attrs={'class': 'form-select'}),
            'assigned_team': forms.Select(attrs={'class': 'form-select'}),
        }


class CompanySearchForm(forms.Form):
    """Form for searching companies."""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search companies...'
        })
    )
    company_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Company.COMPANY_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Company.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    industry = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Industry'
        })
    )


class SalesLeadSearchForm(forms.Form):
    """Form for searching sales leads."""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search leads...'
        })
    )
    lead_source = forms.ChoiceField(
        choices=[('', 'All Sources')] + SalesLead.LEAD_SOURCES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    priority = forms.ChoiceField(
        choices=[('', 'All Priorities')] + SalesLead.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Company.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True),
        required=False,
        empty_label="All Sales Reps",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
