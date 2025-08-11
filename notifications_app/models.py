"""
Notification management models for Inspora platform.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from simple_history.models import HistoricalRecords

User = get_user_model()


class Notification(models.Model):
    """
    Individual notification model.
    """
    NOTIFICATION_TYPES = [
        ('task_assigned', 'Task Assigned'),
        ('task_completed', 'Task Completed'),
        ('task_overdue', 'Task Overdue'),
        ('project_update', 'Project Update'),
        ('goal_update', 'Goal Update'),
        ('comment_added', 'Comment Added'),
        ('mention', 'Mention'),
        ('approval_required', 'Approval Required'),
        ('reminder', 'Reminder'),
        ('system', 'System'),
        ('custom', 'Custom'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Basic notification information
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='custom')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    
    # Notification settings
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    
    # Notification data
    data = models.JSONField(default=dict, blank=True)  # Additional context data
    action_url = models.URLField(blank=True)  # URL for action button
    
    # Relationships
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    
    # Generic foreign key for related object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
    
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"
    
    def get_absolute_url(self):
        return reverse('notifications_app:notification_detail', kwargs={'pk': self.pk})
    
    def mark_as_read(self):
        """Mark notification as read."""
        from django.utils import timezone
        
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def mark_as_sent(self):
        """Mark notification as sent."""
        from django.utils import timezone
        
        if not self.is_sent:
            self.is_sent = True
            self.sent_at = timezone.now()
            self.save(update_fields=['is_sent', 'sent_at'])
    
    def get_related_object(self):
        """Get the related object if content_type and object_id are set."""
        if self.content_type and self.object_id:
            try:
                return self.content_type.get_object_for_this_type(id=self.object_id)
            except:
                return None
        return None


class NotificationTemplate(models.Model):
    """
    Templates for creating notifications.
    """
    TEMPLATE_TYPES = [
        ('email', 'Email'),
        ('push', 'Push'),
        ('in_app', 'In-App'),
        ('sms', 'SMS'),
        ('webhook', 'Webhook'),
    ]
    
    # Template information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, default='in_app')
    
    # Template content
    subject = models.CharField(max_length=200, blank=True)  # For email notifications
    title_template = models.CharField(max_length=200)
    message_template = models.TextField()
    
    # Template settings
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    # Template variables
    variables = models.JSONField(default=list, blank=True)  # Available template variables
    default_data = models.JSONField(default=dict, blank=True)  # Default values for variables
    
    # Relationships
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_notification_templates')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = _('Notification Template')
        verbose_name_plural = _('Notification Templates')
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('notifications_app:template_detail', kwargs={'pk': self.pk})
    
    def render_template(self, context_data):
        """Render template with context data."""
        title = self.title_template
        message = self.message_template
        
        # Simple variable substitution (can be enhanced with proper templating engine)
        for key, value in context_data.items():
            placeholder = f"{{{{{key}}}}}"
            title = title.replace(placeholder, str(value))
            message = message.replace(placeholder, str(value))
        
        return {
            'title': title,
            'message': message
        }


class NotificationChannel(models.Model):
    """
    Different channels for sending notifications.
    """
    CHANNEL_TYPES = [
        ('email', 'Email'),
        ('push', 'Push'),
        ('in_app', 'In-App'),
        ('sms', 'SMS'),
        ('webhook', 'Webhook'),
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
        ('discord', 'Discord'),
    ]
    
    # Channel information
    name = models.CharField(max_length=200)
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPES, default='in_app')
    
    # Channel configuration
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    # Channel settings
    config = models.JSONField(default=dict)  # Channel-specific configuration
    rate_limit = models.PositiveIntegerField(default=100)  # Max notifications per hour
    retry_count = models.PositiveIntegerField(default=3)
    retry_delay = models.PositiveIntegerField(default=60)  # seconds
    
    # Relationships
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_notification_channels')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = _('Notification Channel')
        verbose_name_plural = _('Notification Channels')
    
    def __str__(self):
        return f"{self.name} ({self.get_channel_type_display()})"
    
    def get_absolute_url(self):
        return reverse('notifications_app:channel_detail', kwargs={'pk': self.pk})
    
    def send_notification(self, notification, context_data):
        """Send notification through this channel."""
        try:
            if self.channel_type == 'email':
                return self._send_email(notification, context_data)
            elif self.channel_type == 'push':
                return self._send_push(notification, context_data)
            elif self.channel_type == 'in_app':
                return self._send_in_app(notification, context_data)
            elif self.channel_type == 'webhook':
                return self._send_webhook(notification, context_data)
            else:
                return self._send_custom(notification, context_data)
        except Exception as e:
            # Log error and return False
            return False
    
    def _send_email(self, notification, context_data):
        """Send email notification."""
        # Implementation for email sending
        pass
    
    def _send_push(self, notification, context_data):
        """Send push notification."""
        # Implementation for push notifications
        pass
    
    def _send_in_app(self, notification, context_data):
        """Send in-app notification."""
        # Implementation for in-app notifications
        pass
    
    def _send_webhook(self, notification, context_data):
        """Send webhook notification."""
        # Implementation for webhook notifications
        pass
    
    def _send_custom(self, notification, context_data):
        """Send custom notification."""
        # Implementation for custom channels
        pass


class NotificationPreference(models.Model):
    """
    User preferences for notifications.
    """
    # Notification types preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    in_app_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    # Specific notification preferences
    task_notifications = models.BooleanField(default=True)
    project_notifications = models.BooleanField(default=True)
    goal_notifications = models.BooleanField(default=True)
    comment_notifications = models.BooleanField(default=True)
    mention_notifications = models.BooleanField(default=True)
    system_notifications = models.BooleanField(default=True)
    
    # Frequency preferences
    notification_frequency = models.CharField(max_length=20, default='immediate', choices=[
        ('immediate', 'Immediate'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ])
    
    # Quiet hours
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    quiet_hours_enabled = models.BooleanField(default=False)
    
    # Relationships
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Notification Preference')
        verbose_name_plural = _('Notification Preferences')
    
    def __str__(self):
        return f"Notification preferences for {self.user.username}"
    
    def get_absolute_url(self):
        return reverse('notifications_app:preferences_detail', kwargs={'pk': self.pk})
    
    def is_quiet_hours(self):
        """Check if current time is within quiet hours."""
        if not self.quiet_hours_enabled:
            return False
        
        from django.utils import timezone
        now = timezone.now().time()
        
        if self.quiet_hours_start and self.quiet_hours_end:
            if self.quiet_hours_start <= self.quiet_hours_end:
                return self.quiet_hours_start <= now <= self.quiet_hours_end
            else:  # Crosses midnight
                return now >= self.quiet_hours_start or now <= self.quiet_hours_end
        
        return False


class NotificationGroup(models.Model):
    """
    Group notifications for batch processing.
    """
    # Group information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Group settings
    is_active = models.BooleanField(default=True)
    batch_size = models.PositiveIntegerField(default=100)
    batch_delay = models.PositiveIntegerField(default=300)  # seconds
    
    # Group configuration
    group_config = models.JSONField(default=dict)
    
    # Relationships
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_notification_groups')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = _('Notification Group')
        verbose_name_plural = _('Notification Groups')
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('notifications_app:group_detail', kwargs={'pk': self.pk})
    
    def get_notifications_count(self):
        """Get count of notifications in this group."""
        return self.notifications.count()
