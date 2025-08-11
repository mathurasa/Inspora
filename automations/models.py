"""
Workflow automation models for Inspora platform.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords
from accounts.models import Team

User = get_user_model()


class Automation(models.Model):
    """
    Main automation model for workflow rules.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    # Basic automation information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Automation settings
    is_active = models.BooleanField(default=True)
    is_template = models.BooleanField(default=False)
    allow_manual_trigger = models.BooleanField(default=False)
    
    # Automation behavior
    max_executions_per_hour = models.PositiveIntegerField(default=100)
    execution_timeout = models.PositiveIntegerField(default=300)  # seconds
    
    # Relationships
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_automations')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='automations', null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_executed = models.DateTimeField(null=True, blank=True)
    execution_count = models.PositiveIntegerField(default=0)
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = _('Automation')
        verbose_name_plural = _('Automations')
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('automations:automation_detail', kwargs={'pk': self.pk})
    
    def get_rules_count(self):
        """Get count of automation rules."""
        return self.rules.count()
    
    def get_actions_count(self):
        """Get count of automation actions."""
        return self.actions.count()
    
    def increment_execution_count(self):
        """Increment the execution count."""
        self.execution_count += 1
        self.last_executed = models.DateTimeField(auto_now=True)
        self.save(update_fields=['execution_count', 'last_executed'])


class AutomationRule(models.Model):
    """
    Rules that determine when an automation should trigger.
    """
    RULE_TYPES = [
        ('event', 'Event'),
        ('condition', 'Condition'),
        ('schedule', 'Schedule'),
        ('webhook', 'Webhook'),
        ('manual', 'Manual'),
    ]
    
    # Rule information
    name = models.CharField(max_length=200)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES, default='event')
    
    # Rule configuration
    rule_config = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    
    # Rule logic
    conditions = models.JSONField(default=list, blank=True)  # Multiple conditions
    operator = models.CharField(max_length=10, default='AND', choices=[
        ('AND', 'AND'),
        ('OR', 'OR'),
    ])
    
    # Relationships
    automation = models.ForeignKey(Automation, on_delete=models.CASCADE, related_name='rules')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_automation_rules')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = _('Automation Rule')
        verbose_name_plural = _('Automation Rules')
    
    def __str__(self):
        return f"{self.automation.name} - {self.name}"
    
    def evaluate_conditions(self, context):
        """Evaluate rule conditions against context."""
        if not self.conditions:
            return True
        
        results = []
        for condition in self.conditions:
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')
            
            if field in context:
                context_value = context[field]
                result = self._evaluate_condition(context_value, operator, value)
                results.append(result)
            else:
                results.append(False)
        
        if self.operator == 'AND':
            return all(results)
        else:  # OR
            return any(results)
    
    def _evaluate_condition(self, context_value, operator, value):
        """Evaluate a single condition."""
        if operator == 'equals':
            return context_value == value
        elif operator == 'not_equals':
            return context_value != value
        elif operator == 'contains':
            return str(value) in str(context_value)
        elif operator == 'not_contains':
            return str(value) not in str(context_value)
        elif operator == 'greater_than':
            return context_value > value
        elif operator == 'less_than':
            return context_value < value
        elif operator == 'is_empty':
            return not context_value
        elif operator == 'is_not_empty':
            return bool(context_value)
        return False


class AutomationAction(models.Model):
    """
    Actions to execute when automation rules are met.
    """
    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('notify', 'Notify'),
        ('assign', 'Assign'),
        ('move', 'Move'),
        ('webhook', 'Webhook'),
        ('custom', 'Custom'),
    ]
    
    # Action information
    name = models.CharField(max_length=200)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES, default='notify')
    
    # Action configuration
    action_config = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    
    # Action execution
    order = models.PositiveIntegerField(default=0)
    delay_seconds = models.PositiveIntegerField(default=0)
    retry_count = models.PositiveIntegerField(default=0)
    retry_delay = models.PositiveIntegerField(default=60)  # seconds
    
    # Relationships
    automation = models.ForeignKey(Automation, on_delete=models.CASCADE, related_name='actions')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_automation_actions')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = _('Automation Action')
        verbose_name_plural = _('Automation Actions')
    
    def __str__(self):
        return f"{self.automation.name} - {self.name}"
    
    def execute(self, context):
        """Execute the automation action."""
        try:
            if self.action_type == 'create':
                return self._execute_create(context)
            elif self.action_type == 'update':
                return self._execute_update(context)
            elif self.action_type == 'notify':
                return self._execute_notify(context)
            elif self.action_type == 'assign':
                return self._execute_assign(context)
            elif self.action_type == 'webhook':
                return self._execute_webhook(context)
            else:
                return self._execute_custom(context)
        except Exception as e:
            # Log error and return False
            return False
    
    def _execute_create(self, context):
        """Execute create action."""
        # Implementation for creating new objects
        pass
    
    def _execute_update(self, context):
        """Execute update action."""
        # Implementation for updating existing objects
        pass
    
    def _execute_notify(self, context):
        """Execute notification action."""
        # Implementation for sending notifications
        pass
    
    def _execute_assign(self, context):
        """Execute assignment action."""
        # Implementation for assigning tasks/users
        pass
    
    def _execute_webhook(self, context):
        """Execute webhook action."""
        # Implementation for webhook calls
        pass
    
    def _execute_custom(self, context):
        """Execute custom action."""
        # Implementation for custom actions
        pass


class AutomationTrigger(models.Model):
    """
    Triggers that start automation workflows.
    """
    TRIGGER_TYPES = [
        ('on_create', 'On Create'),
        ('on_update', 'On Update'),
        ('on_delete', 'On Delete'),
        ('on_status_change', 'On Status Change'),
        ('on_field_change', 'On Field Change'),
        ('on_schedule', 'On Schedule'),
        ('on_webhook', 'On Webhook'),
        ('manual', 'Manual'),
    ]
    
    # Trigger information
    name = models.CharField(max_length=200)
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_TYPES, default='on_create')
    
    # Trigger configuration
    trigger_config = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    
    # Trigger conditions
    model_name = models.CharField(max_length=100, blank=True)  # Django model name
    field_name = models.CharField(max_length=100, blank=True)  # Field to monitor
    field_value = models.TextField(blank=True)  # Value to trigger on
    
    # Schedule settings (for scheduled triggers)
    schedule_cron = models.CharField(max_length=100, blank=True)  # Cron expression
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Relationships
    automation = models.ForeignKey(Automation, on_delete=models.CASCADE, related_name='triggers')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_automation_triggers')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    trigger_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = _('Automation Trigger')
        verbose_name_plural = _('Automation Triggers')
    
    def __str__(self):
        return f"{self.automation.name} - {self.name}"
    
    def should_trigger(self, context):
        """Determine if trigger should fire based on context."""
        if not self.is_active:
            return False
        
        if self.trigger_type == 'on_create':
            return context.get('action') == 'create'
        elif self.trigger_type == 'on_update':
            return context.get('action') == 'update'
        elif self.trigger_type == 'on_status_change':
            return self._check_status_change(context)
        elif self.trigger_type == 'on_field_change':
            return self._check_field_change(context)
        elif self.trigger_type == 'on_schedule':
            return self._check_schedule()
        
        return False
    
    def _check_status_change(self, context):
        """Check if status has changed."""
        if 'old_status' in context and 'new_status' in context:
            return context['old_status'] != context['new_status']
        return False
    
    def _check_field_change(self, context):
        """Check if specific field has changed."""
        if 'field_changes' in context:
            return self.field_name in context['field_changes']
        return False
    
    def _check_schedule(self):
        """Check if scheduled trigger should fire."""
        # Implementation for cron-based scheduling
        pass
    
    def increment_trigger_count(self):
        """Increment the trigger count."""
        self.trigger_count += 1
        self.last_triggered = models.DateTimeField(auto_now=True)
        self.save(update_fields=['trigger_count', 'last_triggered'])


class AutomationExecution(models.Model):
    """
    Track automation executions for monitoring and debugging.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Execution information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Execution details
    execution_time = models.FloatField(null=True, blank=True)  # seconds
    error_message = models.TextField(blank=True)
    execution_log = models.JSONField(default=list, blank=True)
    
    # Relationships
    automation = models.ForeignKey(Automation, on_delete=models.CASCADE, related_name='executions')
    triggered_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='triggered_automations', null=True, blank=True)
    
    # Context
    trigger_context = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = _('Automation Execution')
        verbose_name_plural = _('Automation Executions')
    
    def __str__(self):
        return f"Execution {self.id} of {self.automation.name}"
    
    def complete(self, success=True, error_message=''):
        """Mark execution as completed."""
        from django.utils import timezone
        
        self.status = 'completed' if success else 'failed'
        self.completed_at = timezone.now()
        self.error_message = error_message
        
        if self.started_at and self.completed_at:
            self.execution_time = (self.completed_at - self.started_at).total_seconds()
        
        self.save()
    
    def add_log_entry(self, message, level='info'):
        """Add a log entry to the execution log."""
        from django.utils import timezone
        
        log_entry = {
            'timestamp': timezone.now().isoformat(),
            'level': level,
            'message': message
        }
        
        self.execution_log.append(log_entry)
        self.save(update_fields=['execution_log'])
