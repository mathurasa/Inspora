"""
Admin configuration for admin_system app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Company, CompanyMember, SalesLead, Invoice, 
    WorkflowTemplate, WorkflowInstance, AdminDashboard, SystemSettings
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'company_type', 'status', 'company_size', 
        'annual_revenue', 'sales_rep', 'member_count', 'project_count', 'is_active', 'created_at'
    ]
    list_filter = [
        'company_type', 'status', 'industry', 'is_active', 
        'created_at', 'subscription_start'
    ]
    search_fields = ['name', 'website', 'email', 'industry']
    list_editable = ['status', 'is_active']
    readonly_fields = ['member_count', 'project_count', 'total_revenue', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'company_type', 'status', 'industry', 'company_size', 'annual_revenue', 'founded_year')
        }),
        ('Contact Information', {
            'fields': ('website', 'phone', 'email', 'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Sales Information', {
            'fields': ('lead_source', 'sales_rep', 'conversion_date', 'subscription_plan', 'subscription_start', 'subscription_end', 'monthly_recurring_revenue')
        }),
        ('Company Settings', {
            'fields': ('is_active', 'allow_guest_access', 'max_users', 'max_projects')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
    
    def member_count(self, obj):
        return obj.get_member_count()
    member_count.short_description = 'Members'
    
    def project_count(self, obj):
        return obj.get_project_count()
    project_count.short_description = 'Projects'
    
    def total_revenue(self, obj):
        return f"${obj.get_total_revenue():,.2f}"
    total_revenue.short_description = 'Total Revenue'


@admin.register(CompanyMember)
class CompanyMemberAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'company', 'role', 'is_active', 'joined_at', 
        'permissions_summary'
    ]
    list_filter = ['role', 'is_active', 'company', 'joined_at']
    search_fields = ['user__username', 'user__email', 'company__name']
    list_editable = ['role', 'is_active']
    readonly_fields = ['joined_at', 'updated_at']
    
    fieldsets = (
        ('Membership', {
            'fields': ('user', 'company', 'role', 'is_active')
        }),
        ('Permissions', {
            'fields': (
                'can_manage_company', 'can_manage_users', 'can_manage_projects',
                'can_manage_billing', 'can_view_analytics', 'can_export_data'
            )
        }),
        ('Metadata', {
            'fields': ('joined_at', 'updated_at')
        }),
    )
    
    def permissions_summary(self, obj):
        perms = []
        if obj.can_manage_company:
            perms.append('Company')
        if obj.can_manage_users:
            perms.append('Users')
        if obj.can_manage_projects:
            perms.append('Projects')
        if obj.can_manage_billing:
            perms.append('Billing')
        if obj.can_view_analytics:
            perms.append('Analytics')
        if obj.can_export_data:
            perms.append('Export')
        return ', '.join(perms) if perms else 'None'
    permissions_summary.short_description = 'Permissions'


@admin.register(SalesLead)
class SalesLeadAdmin(admin.ModelAdmin):
    list_display = [
        'company_name', 'contact_person', 'lead_source', 'priority', 
        'status', 'estimated_value', 'assigned_to', 'next_follow_up', 'created_at'
    ]
    list_filter = [
        'lead_source', 'priority', 'status', 'assigned_to', 
        'created_at', 'next_follow_up'
    ]
    search_fields = ['company_name', 'contact_person', 'email', 'notes']
    list_editable = ['status', 'priority', 'assigned_to', 'next_follow_up']
    readonly_fields = ['contact_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Lead Information', {
            'fields': ('company_name', 'contact_person', 'email', 'phone')
        }),
        ('Lead Details', {
            'fields': ('lead_source', 'priority', 'estimated_value', 'status', 'notes')
        }),
        ('Assignment & Follow-up', {
            'fields': ('assigned_to', 'next_follow_up', 'last_contact', 'contact_count')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
    
    actions = ['mark_as_qualified', 'mark_as_customer', 'schedule_follow_up']
    
    def mark_as_qualified(self, request, queryset):
        updated = queryset.update(status='qualified')
        self.message_user(request, f'{updated} leads marked as qualified.')
    mark_as_qualified.short_description = 'Mark selected leads as qualified'
    
    def mark_as_customer(self, request, queryset):
        updated = queryset.update(status='customer')
        self.message_user(request, f'{updated} leads converted to customers.')
    mark_as_customer.short_description = 'Convert selected leads to customers'
    
    def schedule_follow_up(self, request, queryset):
        from datetime import timedelta
        from django.utils import timezone
        next_week = timezone.now() + timedelta(days=7)
        updated = queryset.update(next_follow_up=next_week)
        self.message_user(request, f'{updated} leads scheduled for follow-up next week.')
    schedule_follow_up.short_description = 'Schedule follow-up for next week'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number', 'company', 'amount', 'tax_amount', 'total_amount',
        'status', 'issue_date', 'due_date', 'paid_date', 'created_at'
    ]
    list_filter = ['status', 'company', 'issue_date', 'due_date', 'created_at']
    search_fields = ['invoice_number', 'company__name', 'notes']
    list_editable = ['status', 'due_date']
    readonly_fields = ['total_amount', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'company', 'status')
        }),
        ('Billing Details', {
            'fields': ('amount', 'tax_amount', 'total_amount')
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date', 'paid_date')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
    
    actions = ['mark_as_sent', 'mark_as_paid', 'mark_as_overdue']
    
    def mark_as_sent(self, request, queryset):
        updated = queryset.update(status='sent')
        self.message_user(request, f'{updated} invoices marked as sent.')
    mark_as_sent.short_description = 'Mark selected invoices as sent'
    
    def mark_as_paid(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='paid', paid_date=timezone.now().date())
        self.message_user(request, f'{updated} invoices marked as paid.')
    mark_as_paid.short_description = 'Mark selected invoices as paid'
    
    def mark_as_overdue(self, request, queryset):
        updated = queryset.update(status='overdue')
        self.message_user(request, f'{updated} invoices marked as overdue.')
    mark_as_overdue.short_description = 'Mark selected invoices as overdue'


@admin.register(WorkflowTemplate)
class WorkflowTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'workflow_type', 'is_public', 'is_featured', 'is_active',
        'usage_count', 'estimated_duration', 'company', 'created_at'
    ]
    list_filter = [
        'workflow_type', 'is_public', 'is_featured', 'is_active', 
        'company', 'created_at'
    ]
    search_fields = ['name', 'description', 'company__name']
    list_editable = ['is_public', 'is_featured', 'is_active']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'description', 'workflow_type')
        }),
        ('Template Settings', {
            'fields': ('is_public', 'is_featured', 'is_active', 'estimated_duration')
        }),
        ('Workflow Structure', {
            'fields': ('workflow_data',)
        }),
        ('Relationships', {
            'fields': ('company',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'workflow_template', 'company', 'status', 'progress',
        'owner', 'assigned_team', 'start_date', 'target_date', 'created_at'
    ]
    list_filter = [
        'status', 'workflow_template__workflow_type', 'company', 
        'assigned_team', 'created_at'
    ]
    search_fields = ['name', 'company__name', 'owner__username']
    list_editable = ['status', 'progress']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Instance Information', {
            'fields': ('name', 'workflow_template', 'company')
        }),
        ('Status & Progress', {
            'fields': ('status', 'progress', 'current_stage')
        }),
        ('Timeline', {
            'fields': ('start_date', 'target_date', 'completion_date')
        }),
        ('Assignment', {
            'fields': ('owner', 'assigned_team')
        }),
        ('Workflow Data', {
            'fields': ('workflow_data',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(AdminDashboard)
class AdminDashboardAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'is_default', 'accessible_by_count', 
        'accessible_companies_count', 'created_at'
    ]
    list_filter = ['is_default', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_default']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Dashboard Information', {
            'fields': ('name', 'description')
        }),
        ('Configuration', {
            'fields': ('dashboard_config', 'is_default')
        }),
        ('Access Control', {
            'fields': ('accessible_by', 'accessible_companies')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
    
    def accessible_by_count(self, obj):
        return obj.accessible_by.count()
    accessible_by_count.short_description = 'Users'
    
    def accessible_companies_count(self, obj):
        return obj.accessible_companies.count()
    accessible_companies_count.short_description = 'Companies'


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'key', 'value_preview', 'is_public', 'requires_admin', 
        'updated_by', 'updated_at'
    ]
    list_filter = ['is_public', 'requires_admin', 'updated_at']
    search_fields = ['key', 'description']
    list_editable = ['is_public', 'requires_admin']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Setting Information', {
            'fields': ('key', 'value', 'description')
        }),
        ('Access Control', {
            'fields': ('is_public', 'requires_admin')
        }),
        ('Metadata', {
            'fields': ('updated_by', 'created_at', 'updated_at')
        }),
    )
    
    def value_preview(self, obj):
        value_str = str(obj.value)
        if len(value_str) > 50:
            return value_str[:50] + '...'
        return value_str
    value_preview.short_description = 'Value Preview'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only for new objects
            obj.updated_by = request.user
        else:
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)
