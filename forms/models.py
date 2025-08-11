"""
Dynamic forms models for Inspora platform.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords
from accounts.models import Team

User = get_user_model()


class DynamicForm(models.Model):
    """
    Dynamic form model for creating custom forms.
    """
    FORM_TYPES = [
        ('project_request', 'Project Request'),
        ('task_submission', 'Task Submission'),
        ('feedback', 'Feedback'),
        ('survey', 'Survey'),
        ('approval', 'Approval'),
        ('custom', 'Custom'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ]
    
    # Basic form information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    form_type = models.CharField(max_length=20, choices=FORM_TYPES, default='custom')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Form settings
    is_public = models.BooleanField(default=False)
    allow_anonymous = models.BooleanField(default=False)
    require_login = models.BooleanField(default=True)
    allow_multiple_submissions = models.BooleanField(default=False)
    
    # Form behavior
    auto_approve = models.BooleanField(default=False)
    notification_emails = models.JSONField(default=list, blank=True)
    
    # Form structure
    form_config = models.JSONField(default=dict)  # Form layout and configuration
    validation_rules = models.JSONField(default=dict, blank=True)
    
    # Relationships
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_forms')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='forms', null=True, blank=True)
    template = models.ForeignKey('templates.Template', on_delete=models.SET_NULL, related_name='forms', null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = _('Dynamic Form')
        verbose_name_plural = _('Dynamic Forms')
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('forms:form_detail', kwargs={'pk': self.pk})
    
    def get_submissions_count(self):
        """Get count of form submissions."""
        return self.submissions.count()
    
    def get_fields_count(self):
        """Get count of form fields."""
        return self.fields.count()
    
    def is_active(self):
        """Check if form is currently active."""
        return self.status == 'active'


class FormField(models.Model):
    """
    Fields within a dynamic form.
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
        ('section', 'Section'),
        ('custom', 'Custom'),
    ]
    
    # Field information
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=200)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES, default='text')
    
    # Field settings
    is_required = models.BooleanField(default=False)
    is_unique = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    default_value = models.TextField(blank=True)
    
    # Field options
    options = models.JSONField(default=list, blank=True)  # For select, multiselect, radio
    validation_rules = models.JSONField(default=dict, blank=True)
    conditional_logic = models.JSONField(default=dict, blank=True)  # For branching forms
    
    # Field display
    order = models.PositiveIntegerField(default=0)
    help_text = models.TextField(blank=True)
    placeholder = models.CharField(max_length=200, blank=True)
    css_class = models.CharField(max_length=100, blank=True)
    
    # Relationships
    form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE, related_name='fields')
    parent_field = models.ForeignKey('self', on_delete=models.CASCADE, related_name='child_fields', null=True, blank=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = _('Form Field')
        verbose_name_plural = _('Form Fields')
    
    def __str__(self):
        return f"{self.form.name} - {self.label}"
    
    def get_conditional_fields(self):
        """Get fields that depend on this field."""
        return self.child_fields.all()


class FormSubmission(models.Model):
    """
    Individual form submissions.
    """
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending_changes', 'Pending Changes'),
    ]
    
    # Submission information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Submission metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    
    # Relationships
    form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE, related_name='submissions')
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='form_submissions', null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviewed_submissions', null=True, blank=True)
    
    # Review information
    review_notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = _('Form Submission')
        verbose_name_plural = _('Form Submissions')
    
    def __str__(self):
        return f"Submission {self.id} for {self.form.name}"
    
    def get_absolute_url(self):
        return reverse('forms:submission_detail', kwargs={'pk': self.pk})
    
    def get_responses_count(self):
        """Get count of form responses."""
        return self.responses.count()
    
    def get_field_response(self, field_name):
        """Get response for a specific field."""
        try:
            return self.responses.get(field__name=field_name)
        except FormResponse.DoesNotExist:
            return None


class FormResponse(models.Model):
    """
    Individual field responses within a form submission.
    """
    # Response data
    value = models.TextField()
    
    # Relationships
    submission = models.ForeignKey(FormSubmission, on_delete=models.CASCADE, related_name='responses')
    field = models.ForeignKey(FormField, on_delete=models.CASCADE, related_name='responses')
    
    class Meta:
        unique_together = ['submission', 'field']
        verbose_name = _('Form Response')
        verbose_name_plural = _('Form Responses')
    
    def __str__(self):
        return f"Response for {self.field.label} in submission {self.submission.id}"


class FormWorkflow(models.Model):
    """
    Workflow rules for form processing.
    """
    WORKFLOW_TYPES = [
        ('approval', 'Approval'),
        ('notification', 'Notification'),
        ('assignment', 'Assignment'),
        ('custom', 'Custom'),
    ]
    
    # Workflow information
    name = models.CharField(max_length=200)
    workflow_type = models.CharField(max_length=20, choices=WORKFLOW_TYPES, default='approval')
    
    # Workflow configuration
    workflow_config = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    
    # Relationships
    form = models.ForeignKey(DynamicForm, on_delete=models.CASCADE, related_name='workflows')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_form_workflows')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Form Workflow')
        verbose_name_plural = _('Form Workflows')
    
    def __str__(self):
        return f"{self.form.name} - {self.name}"


class FormTemplate(models.Model):
    """
    Template for creating new forms.
    """
    # Template information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Template settings
    is_public = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    usage_count = models.PositiveIntegerField(default=0)
    
    # Template structure
    template_config = models.JSONField(default=dict)
    default_fields = models.JSONField(default=list)
    default_workflow = models.JSONField(default=dict)
    
    # Relationships
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_form_templates')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='form_templates', null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-usage_count', '-created_at']
        verbose_name = _('Form Template')
        verbose_name_plural = _('Form Templates')
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('forms:template_detail', kwargs={'pk': self.pk})
    
    def increment_usage(self):
        """Increment the usage count."""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
