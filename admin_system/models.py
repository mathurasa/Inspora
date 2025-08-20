"""
Admin System models for Inspora platform with sales, company management, and workflow features.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from simple_history.models import HistoricalRecords

User = get_user_model()


class Company(models.Model):
    """
    Company model for managing different organizations using the platform.
    """
    COMPANY_TYPES = [
        ('startup', 'Startup'),
        ('sme', 'Small & Medium Enterprise'),
        ('enterprise', 'Enterprise'),
        ('agency', 'Agency'),
        ('consulting', 'Consulting'),
        ('nonprofit', 'Non-Profit'),
        ('education', 'Education'),
        ('healthcare', 'Healthcare'),
        ('financial', 'Financial Services'),
        ('manufacturing', 'Manufacturing'),
        ('retail', 'Retail'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('prospect', 'Prospect'),
        ('lead', 'Lead'),
        ('qualified', 'Qualified'),
        ('customer', 'Customer'),
        ('churned', 'Churned'),
        ('inactive', 'Inactive'),
    ]
    
    # Basic company information
    name = models.CharField(max_length=200, unique=True)
    company_type = models.CharField(max_length=20, choices=COMPANY_TYPES, default='other')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='prospect')
    
    # Contact information
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    # Address
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='United States')
    
    # Company details
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.PositiveIntegerField(help_text='Number of employees', null=True, blank=True)
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    
    # Sales information
    lead_source = models.CharField(max_length=100, blank=True)
    sales_rep = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='assigned_companies', null=True, blank=True)
    conversion_date = models.DateField(null=True, blank=True)
    
    # Subscription details
    subscription_plan = models.CharField(max_length=50, blank=True)
    subscription_start = models.DateField(null=True, blank=True)
    subscription_end = models.DateField(null=True)
    monthly_recurring_revenue = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Company settings
    is_active = models.BooleanField(default=True)
    allow_guest_access = models.BooleanField(default=False)
    max_users = models.PositiveIntegerField(default=10)
    max_projects = models.PositiveIntegerField(default=50)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_companies')
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('admin_system:company_detail', kwargs={'pk': self.pk})
    
    def get_member_count(self):
        """Return the number of active members in the company."""
        return self.company_members.filter(is_active=True).count()
    
    def get_project_count(self):
        """Return the number of active projects in the company."""
        return self.projects.filter(status__in=['planning', 'active', 'on_hold']).count()
    
    def get_total_revenue(self):
        """Calculate total revenue from this company."""
        return self.invoices.filter(status='paid').aggregate(
            total=models.Sum('amount')
        )['total'] or 0


class CompanyMember(models.Model):
    """
    Company membership model for managing users within companies.
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
        ('guest', 'Guest'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='company_memberships')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_members')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    
    # Permissions
    can_manage_company = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_manage_projects = models.BooleanField(default=False)
    can_manage_billing = models.BooleanField(default=False)
    can_view_analytics = models.BooleanField(default=False)
    can_export_data = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'company']
        ordering = ['company', 'role', 'user__username']
        verbose_name = _('Company Member')
        verbose_name_plural = _('Company Members')
    
    def __str__(self):
        return f"{self.user.username} - {self.company.name} ({self.role})"
    
    def save(self, *args, **kwargs):
        # Set permissions based on role
        if self.role == 'owner':
            self.can_manage_company = True
            self.can_manage_users = True
            self.can_manage_projects = True
            self.can_manage_billing = True
            self.can_view_analytics = True
            self.can_export_data = True
        elif self.role == 'admin':
            self.can_manage_users = True
            self.can_manage_projects = True
            self.can_view_analytics = True
            self.can_export_data = True
        elif self.role == 'manager':
            self.can_manage_projects = True
            self.can_view_analytics = True
        elif self.role == 'member':
            self.can_view_analytics = True
        
        super().save(*args, **kwargs)


class SalesLead(models.Model):
    """
    Sales lead model for tracking potential customers.
    """
    LEAD_SOURCES = [
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('social_media', 'Social Media'),
        ('email_campaign', 'Email Campaign'),
        ('cold_outreach', 'Cold Outreach'),
        ('event', 'Event'),
        ('advertisement', 'Advertisement'),
        ('other', 'Other'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Lead information
    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # Lead details
    lead_source = models.CharField(max_length=20, choices=LEAD_SOURCES, default='website')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    estimated_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Lead status
    status = models.CharField(max_length=20, choices=Company.STATUS_CHOICES, default='prospect')
    notes = models.TextField(blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='assigned_leads', null=True, blank=True)
    
    # Follow-up
    next_follow_up = models.DateTimeField(null=True, blank=True)
    last_contact = models.DateTimeField(null=True, blank=True)
    contact_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_leads')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Sales Lead')
        verbose_name_plural = _('Sales Leads')
    
    def __str__(self):
        return f"{self.company_name} - {self.contact_person}"
    
    def get_absolute_url(self):
        return reverse('admin_system:lead_detail', kwargs={'pk': self.pk})


class Invoice(models.Model):
    """
    Invoice model for billing companies.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Invoice information
    invoice_number = models.CharField(max_length=50, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='invoices')
    
    # Billing details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Dates
    issue_date = models.DateField()
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_invoices')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.company.name}"
    
    def get_absolute_url(self):
        return reverse('admin_system:invoice_detail', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        # Calculate total amount
        self.total_amount = self.amount + self.tax_amount
        super().save(*args, **kwargs)


class WorkflowTemplate(models.Model):
    """
    Workflow template model for creating Asana-like project workflows.
    """
    WORKFLOW_TYPES = [
        ('project_management', 'Project Management'),
        ('task_management', 'Task Management'),
        ('approval_process', 'Approval Process'),
        ('onboarding', 'Onboarding'),
        ('marketing_campaign', 'Marketing Campaign'),
        ('product_development', 'Product Development'),
        ('customer_support', 'Customer Support'),
        ('sales_process', 'Sales Process'),
        ('hr_process', 'HR Process'),
        ('custom', 'Custom'),
    ]
    
    # Template information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    workflow_type = models.CharField(max_length=30, choices=WORKFLOW_TYPES, default='custom')
    
    # Template settings
    is_public = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    
    # Workflow structure
    workflow_data = models.JSONField(default=dict)  # Contains stages, tasks, dependencies
    estimated_duration = models.PositiveIntegerField(help_text='Estimated duration in days', null=True, blank=True)
    
    # Relationships
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_workflows')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='workflow_templates', null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-usage_count', '-created_at']
        verbose_name = _('Workflow Template')
        verbose_name_plural = _('Workflow Templates')
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('admin_system:workflow_template_detail', kwargs={'pk': self.pk})


class WorkflowInstance(models.Model):
    """
    Workflow instance model for running workflow templates.
    """
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Instance information
    name = models.CharField(max_length=200)
    workflow_template = models.ForeignKey(WorkflowTemplate, on_delete=models.CASCADE, related_name='instances')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='workflows')
    
    # Status and progress
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    progress = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Dates
    start_date = models.DateField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    
    # Assignment
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_workflows')
    assigned_team = models.ForeignKey('accounts.Team', on_delete=models.SET_NULL, related_name='assigned_workflows', null=True, blank=True)
    
    # Workflow data
    current_stage = models.CharField(max_length=100, blank=True)
    workflow_data = models.JSONField(default=dict)  # Current state of the workflow
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Workflow Instance')
        verbose_name_plural = _('Workflow Instances')
    
    def __str__(self):
        return f"{self.name} - {self.company.name}"
    
    def get_absolute_url(self):
        return reverse('admin_system:workflow_instance_detail', kwargs={'pk': self.pk})


class AdminDashboard(models.Model):
    """
    Admin dashboard configuration model for customizing admin views.
    """
    # Dashboard information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Dashboard configuration
    dashboard_config = models.JSONField(default=dict)  # Widgets, layout, permissions
    is_default = models.BooleanField(default=False)
    
    # Access control
    accessible_by = models.ManyToManyField(User, related_name='accessible_dashboards')
    accessible_companies = models.ManyToManyField(Company, related_name='accessible_dashboards')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_dashboards')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Admin Dashboard')
        verbose_name_plural = _('Admin Dashboards')
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('admin_system:admin_dashboard_detail', kwargs={'pk': self.pk})


class SystemSettings(models.Model):
    """
    System-wide settings model for platform configuration.
    """
    # Setting information
    key = models.CharField(max_length=100, unique=True)
    value = models.JSONField()
    description = models.TextField(blank=True)
    
    # Access control
    is_public = models.BooleanField(default=False)
    requires_admin = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_settings')
    
    class Meta:
        ordering = ['key']
        verbose_name = _('System Setting')
        verbose_name_plural = _('System Settings')
    
    def __str__(self):
        return self.key
    
    @classmethod
    def get_setting(cls, key, default=None):
        """Get a system setting value."""
        try:
            setting = cls.objects.get(key=key)
            return setting.value
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_setting(cls, key, value, description='', updated_by=None):
        """Set a system setting value."""
        setting, created = cls.objects.get_or_create(
            key=key,
            defaults={'value': value, 'description': description}
        )
        if not created:
            setting.value = value
            setting.description = description
            if updated_by:
                setting.updated_by = updated_by
            setting.save()
        return setting
