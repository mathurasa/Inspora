from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class Template(models.Model):
    """
    Template model for forms and other content.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    template_type = models.CharField(max_length=50, default='form')
    content = models.JSONField(default=dict)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = _('Template')
        verbose_name_plural = _('Templates')
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('templates:template_detail', kwargs={'pk': self.pk})
