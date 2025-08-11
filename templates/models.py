"""
Template management models for Inspora platform.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords
from accounts.models import Team

User = get_user_model()


class Template(models.Model):
    """
    Base template model for creating reusable structures.
    """
    TEMPLATE_TYPES = [
        ('project', 'Project'),
        ('task', 'Task'),
        ('goal', 'Goal'),
        ('portfolio', 'Portfolio'),
        ('form', 'Form'),
        ('workflow', 'Workflow'),
        ('custom', 'Custom'),
    ]
    
    # Basic template information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, default='custom')
    
    # Template settings
    is_public = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    
    # Template structure
    template_data = models.JSONField(default=dict)
    version = models.CharField(max_length=20, default='1.0.0')
    
    # Relationships
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_templates')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='templates', null=True, blank=True)
    category = models.ForeignKey('TemplateCategory', on_delete=models.SET_NULL, related_name='templates', null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-usage_count', '-created_at']
        verbose_name = _('Template')
        verbose_name_plural = _('Templates')
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('templates:template_detail', kwargs={'pk': self.pk})
    
    def increment_usage(self):
        """Increment the usage count."""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
    
    def get_template_fields(self):
        """Get template fields from template_data."""
        return self.template_data.get('fields', [])
    
    def get_template_sections(self):
        """Get template sections from template_data."""
        return self.template_data.get('sections', [])
    
    def get_template_workflow(self):
        """Get template workflow from template_data."""
        return self.template_data.get('workflow', {})


class TemplateField(models.Model):
    """
    Fields within a template.
    """
    FIELD_TYPES = [
        ('text', 'Text'),
        ('textarea', 'Text Area'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('datetime', 'Date & Time'),
        ('select', 'Select'),
        ('multiselect', 'Multi Select'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio'),
        ('file', 'File'),
        ('url', 'URL'),
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('custom', 'Custom'),
    ]
    
    # Field information
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=200)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES, default='text')
    
    # Field settings
    is_required = models.BooleanField(default=False)
    is_unique = models.BooleanField(default=False)
    default_value = models.TextField(blank=True)
    
    # Field options
    options = models.JSONField(default=list, blank=True)  # For select, multiselect, radio
    validation_rules = models.JSONField(default=dict, blank=True)
    
    # Field display
    order = models.PositiveIntegerField(default=0)
    help_text = models.TextField(blank=True)
    placeholder = models.CharField(max_length=200, blank=True)
    
    # Relationships
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='fields')
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = _('Template Field')
        verbose_name_plural = _('Template Fields')
    
    def __str__(self):
        return f"{self.template.name} - {self.label}"


class TemplateCategory(models.Model):
    """
    Categories for organizing templates.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color
    icon = models.CharField(max_length=50, blank=True)
    
    # Category settings
    is_active = models.BooleanField(default=True)
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, related_name='sub_categories', null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = _('Template Category')
        verbose_name_plural = _('Template Categories')
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('templates:category_detail', kwargs={'pk': self.pk})
    
    def get_templates_count(self):
        """Get count of templates in this category."""
        return self.templates.count()


class TemplateVersion(models.Model):
    """
    Version history for templates.
    """
    # Version information
    version_number = models.CharField(max_length=20)
    changelog = models.TextField(blank=True)
    
    # Template data snapshot
    template_data = models.JSONField()
    
    # Relationships
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='versions')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_template_versions')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    is_current = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['template', 'version_number']
        verbose_name = _('Template Version')
        verbose_name_plural = _('Template Versions')
    
    def __str__(self):
        return f"{self.template.name} v{self.version_number}"
    
    def save(self, *args, **kwargs):
        """Ensure only one version is current."""
        if self.is_current:
            TemplateVersion.objects.filter(template=self.template, is_current=True).update(is_current=False)
        super().save(*args, **kwargs)


class TemplateUsage(models.Model):
    """
    Track template usage for analytics.
    """
    # Usage information
    used_at = models.DateTimeField(auto_now_add=True)
    
    # Relationships
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='usage_records')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='template_usage')
    
    # Usage context
    context = models.JSONField(default=dict, blank=True)  # Additional context about usage
    
    class Meta:
        ordering = ['-used_at']
        verbose_name = _('Template Usage')
        verbose_name_plural = _('Template Usage Records')
    
    def __str__(self):
        return f"{self.template.name} used by {self.user.username} at {self.used_at}"
