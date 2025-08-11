"""
Goal management models for Inspora platform.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from simple_history.models import HistoricalRecords
from accounts.models import Team

User = get_user_model()


class Goal(models.Model):
    """
    Goal model for setting and tracking objectives.
    """
    GOAL_TYPES = [
        ('company', 'Company'),
        ('team', 'Team'),
        ('personal', 'Personal'),
        ('project', 'Project'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('on_track', 'On Track'),
        ('at_risk', 'At Risk'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    # Basic goal information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES, default='personal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Goal details
    target_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    current_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True)  # e.g., "users", "revenue", "tasks"
    
    # Goal timeline
    start_date = models.DateField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    
    # Goal settings
    is_public = models.BooleanField(default=False)
    is_template = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    
    # Relationships
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_goals')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='goals', null=True, blank=True)
    parent_goal = models.ForeignKey('self', on_delete=models.CASCADE, related_name='sub_goals', null=True, blank=True)
    
    # Goal metadata
    tags = models.JSONField(default=list, blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_goals')
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = _('Goal')
        verbose_name_plural = _('Goals')
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('goals:goal_detail', kwargs={'pk': self.pk})
    
    def get_progress_percentage(self):
        """Calculate goal completion percentage."""
        if self.target_value and self.current_value:
            if self.target_value > 0:
                progress = (self.current_value / self.target_value) * 100
                return min(round(progress, 1), 100)
        return 0
    
    def get_sub_goals_count(self):
        """Get count of sub-goals."""
        return self.sub_goals.count()
    
    def get_related_tasks_count(self):
        """Get count of related tasks."""
        from tasks.models import Task
        return Task.objects.filter(goals=self).count()
    
    def is_overdue(self):
        """Check if goal is overdue."""
        from django.utils import timezone
        if self.target_date and self.status not in ['completed', 'cancelled']:
            return self.target_date < timezone.now().date()
        return False
    
    def get_aligned_goals_count(self):
        """Get count of aligned goals."""
        return self.aligned_goals.count()


class GoalProgress(models.Model):
    """
    Track progress updates for goals.
    """
    # Progress information
    current_value = models.DecimalField(max_digits=15, decimal_places=2)
    notes = models.TextField(blank=True)
    
    # Relationships
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='progress_updates')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goal_progress_updates')
    
    # Progress metadata
    confidence_level = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Confidence level from 1-10"
    )
    
    # Timestamps
    updated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = _('Goal Progress')
        verbose_name_plural = _('Goal Progress Updates')
    
    def __str__(self):
        return f"Progress update for {self.goal.title} by {self.updated_by.username}"
    
    def save(self, *args, **kwargs):
        """Update goal's current value when saving progress."""
        super().save(*args, **kwargs)
        self.goal.current_value = self.current_value
        self.goal.save(update_fields=['current_value'])


class GoalAlignment(models.Model):
    """
    Track how goals align with each other.
    """
    ALIGNMENT_TYPES = [
        ('supports', 'Supports'),
        ('conflicts', 'Conflicts'),
        ('depends_on', 'Depends On'),
        ('related', 'Related'),
    ]
    
    # Relationships
    primary_goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='aligned_goals')
    aligned_goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='aligned_from_goals')
    alignment_type = models.CharField(max_length=20, choices=ALIGNMENT_TYPES, default='supports')
    
    # Alignment details
    strength = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Alignment strength from 1-10"
    )
    notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_goal_alignments')
    
    class Meta:
        unique_together = ['primary_goal', 'aligned_goal']
        verbose_name = _('Goal Alignment')
        verbose_name_plural = _('Goal Alignments')
    
    def __str__(self):
        return f"{self.primary_goal.title} {self.get_alignment_type_display()} {self.aligned_goal.title}"


class GoalComment(models.Model):
    """
    Comments on goals for collaboration and discussion.
    """
    content = models.TextField()
    
    # Relationships
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goal_comments')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True)
    
    # Comment settings
    is_internal = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = _('Goal Comment')
        verbose_name_plural = _('Goal Comments')
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.goal.title}"
    
    def get_replies_count(self):
        """Get count of replies to this comment."""
        return self.replies.count()


class GoalTemplate(models.Model):
    """
    Template for creating new goals with predefined structure.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Template settings
    is_public = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    usage_count = models.PositiveIntegerField(default=0)
    
    # Template structure
    default_fields = models.JSONField(default=dict)
    default_metrics = models.JSONField(default=list)
    default_timeline = models.JSONField(default=dict)
    
    # Relationships
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_goal_templates')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='goal_templates', null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-usage_count', '-created_at']
        verbose_name = _('Goal Template')
        verbose_name_plural = _('Goal Templates')
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('goals:template_detail', kwargs={'pk': self.pk})
    
    def increment_usage(self):
        """Increment the usage count."""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
