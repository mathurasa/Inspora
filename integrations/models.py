"""
Integration models for Inspora platform.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Integration(models.Model):
    """
    Base integration model for all third-party services.
    """
    INTEGRATION_TYPES = [
        ('google_drive', 'Google Drive'),
        ('slack', 'Slack'),
        ('github', 'GitHub'),
        ('microsoft_teams', 'Microsoft Teams'),
        ('jira', 'Jira'),
        ('trello', 'Trello'),
        ('asana', 'Asana'),
        ('zapier', 'Zapier'),
        ('webhook', 'Webhook'),
        ('custom', 'Custom Integration'),
    ]
    
    STATUS_CHOICES = [
        ('disconnected', 'Disconnected'),
        ('connecting', 'Connecting'),
        ('connected', 'Connected'),
        ('error', 'Error'),
        ('disconnected', 'Disconnected'),
    ]
    
    name = models.CharField(max_length=100)
    integration_type = models.CharField(max_length=50, choices=INTEGRATION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disconnected')
    
    # Configuration
    config = models.JSONField(default=dict, blank=True)
    credentials = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='integrations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    
    # Settings
    is_active = models.BooleanField(default=True)
    auto_sync = models.BooleanField(default=False)
    sync_interval = models.IntegerField(default=3600, help_text='Sync interval in seconds')
    
    class Meta:
        ordering = ['name']
        verbose_name = _('Integration')
        verbose_name_plural = _('Integrations')
    
    def __str__(self):
        return f"{self.name} ({self.get_integration_type_display()})"
    
    def get_status_badge_class(self):
        """Return Bootstrap badge class for status."""
        status_classes = {
            'connected': 'bg-success',
            'connecting': 'bg-warning',
            'error': 'bg-danger',
            'disconnected': 'bg-secondary',
        }
        return status_classes.get(self.status, 'bg-secondary')
    
    def can_connect(self):
        """Check if integration can be connected."""
        return self.status in ['disconnected', 'error']
    
    def can_disconnect(self):
        """Check if integration can be disconnected."""
        return self.status == 'connected'


class GoogleDriveIntegration(models.Model):
    """
    Google Drive specific integration model.
    """
    integration = models.OneToOneField(Integration, on_delete=models.CASCADE, related_name='google_drive')
    
    # Google OAuth2 credentials
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expiry = models.DateTimeField(null=True, blank=True)
    
    # Drive settings
    root_folder_id = models.CharField(max_length=100, blank=True)
    sync_folders = models.JSONField(default=list, blank=True)
    
    # Permissions
    can_read = models.BooleanField(default=True)
    can_write = models.BooleanField(default=False)
    can_share = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = _('Google Drive Integration')
        verbose_name_plural = _('Google Drive Integrations')
    
    def __str__(self):
        return f"Google Drive - {self.integration.name}"
    
    def is_token_valid(self):
        """Check if the access token is still valid."""
        if not self.token_expiry:
            return False
        from django.utils import timezone
        return timezone.now() < self.token_expiry
    
    def needs_refresh(self):
        """Check if token needs refresh."""
        if not self.token_expiry:
            return True
        from django.utils import timezone
        # Refresh if token expires in next 5 minutes
        return timezone.now() > (self.token_expiry - timezone.timedelta(minutes=5))


class IntegrationLog(models.Model):
    """
    Log for integration activities and errors.
    """
    LOG_LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('success', 'Success'),
    ]
    
    integration = models.ForeignKey(Integration, on_delete=models.CASCADE, related_name='logs')
    level = models.CharField(max_length=20, choices=LOG_LEVELS, default='info')
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('Integration Log')
        verbose_name_plural = _('Integration Logs')
    
    def __str__(self):
        return f"{self.integration.name} - {self.level} - {self.timestamp}"
    
    def get_level_badge_class(self):
        """Return Bootstrap badge class for log level."""
        level_classes = {
            'info': 'bg-info',
            'warning': 'bg-warning',
            'error': 'bg-danger',
            'success': 'bg-success',
        }
        return level_classes.get(self.level, 'bg-secondary')


class IntegrationWebhook(models.Model):
    """
    Webhook configuration for integrations.
    """
    integration = models.ForeignKey(Integration, on_delete=models.CASCADE, related_name='webhooks')
    name = models.CharField(max_length=100)
    url = models.URLField()
    events = models.JSONField(default=list, blank=True)
    headers = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = _('Integration Webhook')
        verbose_name_plural = _('Integration Webhooks')
    
    def __str__(self):
        return f"{self.name} - {self.integration.name}"
