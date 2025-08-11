"""
Project management models for Inspora platform.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from accounts.models import User, Team


class Project(models.Model):
    """
    Project model for organizing work and tasks.
    """
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Dates
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    
    # Ownership
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='projects', null=True, blank=True)
    
    # Progress
    progress = models.PositiveIntegerField(default=0, help_text='Progress percentage (0-100)')
    
    # Project settings
    is_template = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.JSONField(default=list, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('projects:project_detail', kwargs={'pk': self.pk})
    
    def get_progress_percentage(self):
        """Calculate progress percentage based on completed tasks."""
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        
        completed_tasks = self.tasks.filter(status='completed').count()
        return int((completed_tasks / total_tasks) * 100)
    
    def is_overdue(self):
        """Check if project is overdue."""
        if self.due_date and self.status not in ['completed', 'cancelled']:
            from django.utils import timezone
            return timezone.now().date() > self.due_date
        return False


class ProjectSection(models.Model):
    """
    Sections within a project for organizing tasks.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        unique_together = ['project', 'name']
    
    def __str__(self):
        return f"{self.project.name} - {self.name}"


class ProjectMember(models.Model):
    """
    Project team members with roles and permissions.
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('manager', 'Manager'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    
    # Permissions
    can_edit_project = models.BooleanField(default=False)
    can_manage_tasks = models.BooleanField(default=False)
    can_manage_members = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['project', 'user']
        ordering = ['project', 'role', 'user__username']
    
    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.role})"
    
    def save(self, *args, **kwargs):
        # Set permissions based on role
        if self.role == 'owner':
            self.can_edit_project = True
            self.can_manage_tasks = True
            self.can_manage_members = True
        elif self.role == 'manager':
            self.can_edit_project = True
            self.can_manage_tasks = True
        elif self.role == 'member':
            self.can_manage_tasks = True
        
        super().save(*args, **kwargs)
