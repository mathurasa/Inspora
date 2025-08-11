"""
Audit logging models for Inspora platform.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from simple_history.models import HistoricalRecords

User = get_user_model()


class AuditLog(models.Model):
    """
    Main audit log model for tracking system activities.
    """
    EVENT_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('permission_change', 'Permission Change'),
        ('data_access', 'Data Access'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('bulk_action', 'Bulk Action'),
        ('system', 'System'),
        ('custom', 'Custom'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    # Basic audit information
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='custom')
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='low')
    
    # Event details
    description = models.TextField()
    details = models.JSONField(default=dict, blank=True)  # Additional event details
    
    # User and session information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='audit_logs', null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Object information (generic foreign key)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Metadata
    source = models.CharField(max_length=100, blank=True)  # Source of the event
    tags = models.JSONField(default=list, blank=True)  # Tags for categorization
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('Audit Log')
        verbose_name_plural = _('Audit Logs')
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['event_type']),
            models.Index(fields=['user']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.event_type} event by {self.user.username if self.user else 'System'} at {self.timestamp}"
    
    def get_absolute_url(self):
        return reverse('audit:log_detail', kwargs={'pk': self.pk})
    
    def get_related_object(self):
        """Get the related object if content_type and object_id are set."""
        if self.content_type and self.object_id:
            try:
                return self.content_type.get_object_for_this_type(id=self.object_id)
            except:
                return None
        return None


class AuditEvent(models.Model):
    """
    Specific audit events with detailed information.
    """
    # Event information
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True)
    
    # Event data
    before_data = models.JSONField(default=dict, blank=True)  # Data before change
    after_data = models.JSONField(default=dict, blank=True)   # Data after change
    changed_fields = models.JSONField(default=list, blank=True)  # Fields that changed
    
    # Event context
    context = models.JSONField(default=dict, blank=True)  # Additional context
    metadata = models.JSONField(default=dict, blank=True)  # Event metadata
    
    # Relationships
    audit_log = models.ForeignKey(AuditLog, on_delete=models.CASCADE, related_name='events')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Audit Event')
        verbose_name_plural = _('Audit Events')
    
    def __str__(self):
        return f"{self.name} - {self.audit_log.event_type}"
    
    def get_changes_summary(self):
        """Get a summary of what changed."""
        if not self.changed_fields:
            return "No specific changes recorded"
        
        changes = []
        for field in self.changed_fields:
            old_value = self.before_data.get(field, 'N/A')
            new_value = self.after_data.get(field, 'N/A')
            changes.append(f"{field}: {old_value} → {new_value}")
        
        return "; ".join(changes)


class AuditPolicy(models.Model):
    """
    Policies for audit logging configuration.
    """
    POLICY_TYPES = [
        ('retention', 'Retention'),
        ('filtering', 'Filtering'),
        ('alerting', 'Alerting'),
        ('export', 'Export'),
        ('custom', 'Custom'),
    ]
    
    # Policy information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    policy_type = models.CharField(max_length=20, choices=POLICY_TYPES, default='retention')
    
    # Policy configuration
    is_active = models.BooleanField(default=True)
    config = models.JSONField(default=dict)
    
    # Policy scope
    applies_to = models.CharField(max_length=100, blank=True)  # Model or app name
    conditions = models.JSONField(default=dict, blank=True)  # When policy applies
    
    # Relationships
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_audit_policies')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = _('Audit Policy')
        verbose_name_plural = _('Audit Policies')
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('audit:policy_detail', kwargs={'pk': self.pk})
    
    def should_apply(self, context):
        """Determine if policy should apply to given context."""
        if not self.is_active:
            return False
        
        if not self.conditions:
            return True
        
        # Simple condition evaluation (can be enhanced)
        for key, value in self.conditions.items():
            if key in context:
                if context[key] != value:
                    return False
            else:
                return False
        
        return True


class AuditExport(models.Model):
    """
    Audit log exports for compliance and analysis.
    """
    EXPORT_FORMATS = [
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('xml', 'XML'),
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Export information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    export_format = models.CharField(max_length=20, choices=EXPORT_FORMATS, default='csv')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Export configuration
    date_range_start = models.DateTimeField(null=True, blank=True)
    date_range_end = models.DateTimeField(null=True, blank=True)
    filters = models.JSONField(default=dict, blank=True)
    
    # Export results
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    record_count = models.PositiveIntegerField(null=True, blank=True)
    
    # Export metadata
    error_message = models.TextField(blank=True)
    processing_time = models.FloatField(null=True, blank=True)  # seconds
    
    # Relationships
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_audit_exports')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Audit Export')
        verbose_name_plural = _('Audit Exports')
    
    def __str__(self):
        return f"{self.name} ({self.get_export_format_display()})"
    
    def get_absolute_url(self):
        return reverse('audit:export_detail', kwargs={'pk': self.pk})
    
    def mark_completed(self, file_path, record_count, processing_time):
        """Mark export as completed."""
        from django.utils import timezone
        
        self.status = 'completed'
        self.file_path = file_path
        self.record_count = record_count
        self.processing_time = processing_time
        self.completed_at = timezone.now()
        self.save()
    
    def mark_failed(self, error_message):
        """Mark export as failed."""
        self.status = 'failed'
        self.error_message = error_message
        self.save()


class AuditAlert(models.Model):
    """
    Alerts for suspicious or important audit events.
    """
    ALERT_TYPES = [
        ('security', 'Security'),
        ('compliance', 'Compliance'),
        ('performance', 'Performance'),
        ('data_access', 'Data Access'),
        ('permission_change', 'Permission Change'),
        ('custom', 'Custom'),
    ]
    
    SEVERITY_LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    # Alert information
    title = models.CharField(max_length=200)
    message = models.TextField()
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, default='custom')
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='info')
    
    # Alert status
    is_active = models.BooleanField(default=True)
    is_acknowledged = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    
    # Alert data
    alert_data = models.JSONField(default=dict, blank=True)
    related_audit_logs = models.ManyToManyField(AuditLog, blank=True)
    
    # Alert metadata
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='acknowledged_alerts', null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='resolved_alerts', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Audit Alert')
        verbose_name_plural = _('Audit Alerts')
    
    def __str__(self):
        return f"{self.title} ({self.get_severity_display()})"
    
    def get_absolute_url(self):
        return reverse('audit:alert_detail', kwargs={'pk': self.pk})
    
    def acknowledge(self, user):
        """Acknowledge the alert."""
        from django.utils import timezone
        
        self.is_acknowledged = True
        self.acknowledged_by = user
        self.acknowledged_at = timezone.now()
        self.save()
    
    def resolve(self, user):
        """Resolve the alert."""
        from django.utils import timezone
        
        self.is_resolved = True
        self.resolved_by = user
        self.resolved_at = timezone.now()
        self.save()


class AuditDashboard(models.Model):
    """
    Dashboard configurations for audit data visualization.
    """
    # Dashboard information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Dashboard configuration
    config = models.JSONField(default=dict)  # Dashboard layout and widgets
    is_public = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    
    # Dashboard settings
    refresh_interval = models.PositiveIntegerField(default=300)  # seconds
    max_data_points = models.PositiveIntegerField(default=1000)
    
    # Relationships
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_audit_dashboards')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = _('Audit Dashboard')
        verbose_name_plural = _('Audit Dashboards')
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('audit:dashboard_detail', kwargs={'pk': self.pk})
    
    def get_widgets_count(self):
        """Get count of widgets in dashboard."""
        return len(self.config.get('widgets', []))
