from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Integration, IntegrationLog


@receiver(post_save, sender=Integration)
def log_integration_change(sender, instance, created, **kwargs):
    """Log when an integration is created or updated."""
    if created:
        IntegrationLog.objects.create(
            integration=instance,
            level='info',
            message=f'Integration "{instance.name}" created',
            details={'action': 'created', 'integration_type': instance.integration_type}
        )
    else:
        IntegrationLog.objects.create(
            integration=instance,
            level='info',
            message=f'Integration "{instance.name}" updated',
            details={'action': 'updated', 'status': instance.status}
        )


@receiver(post_delete, sender=Integration)
def log_integration_deletion(sender, instance, **kwargs):
    """Log when an integration is deleted."""
    IntegrationLog.objects.create(
        integration=instance,
        level='warning',
        message=f'Integration "{instance.name}" deleted',
        details={'action': 'deleted', 'integration_type': instance.integration_type}
    )


