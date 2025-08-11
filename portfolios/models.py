"""
Portfolio management models for Inspora platform.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords
from accounts.models import Team
from projects.models import Project
from goals.models import Goal

User = get_user_model()


class Portfolio(models.Model):
    """
    Portfolio model for managing multiple projects and goals.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('planning', 'Planning'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    
    # Basic portfolio information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Portfolio details
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Portfolio settings
    is_public = models.BooleanField(default=False)
    allow_guest_access = models.BooleanField(default=False)
    
    # Relationships
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_portfolios')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='portfolios', null=True, blank=True)
    parent_portfolio = models.ForeignKey('self', on_delete=models.CASCADE, related_name='sub_portfolios', null=True, blank=True)
    
    # Portfolio metadata
    tags = models.JSONField(default=list, blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_portfolios')
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = _('Portfolio')
        verbose_name_plural = _('Portfolios')
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('portfolios:portfolio_detail', kwargs={'pk': self.pk})
    
    def get_projects_count(self):
        """Get count of projects in this portfolio."""
        return self.projects.count()
    
    def get_goals_count(self):
        """Get count of goals in this portfolio."""
        return self.goals.count()
    
    def get_progress_percentage(self):
        """Calculate portfolio completion percentage."""
        projects = self.projects.all()
        if not projects:
            return 0
        
        total_progress = sum(project.get_progress_percentage() for project in projects)
        return round(total_progress / len(projects), 1)
    
    def get_budget_utilization(self):
        """Calculate budget utilization percentage."""
        if self.budget and self.actual_cost:
            return round((self.actual_cost / self.budget) * 100, 1)
        return 0


class PortfolioProject(models.Model):
    """
    Projects within a portfolio.
    """
    # Relationships
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='projects')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='portfolios')
    
    # Portfolio project settings
    priority = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='added_portfolio_projects')
    
    class Meta:
        unique_together = ['portfolio', 'project']
        ordering = ['priority', '-added_at']
        verbose_name = _('Portfolio Project')
        verbose_name_plural = _('Portfolio Projects')
    
    def __str__(self):
        return f"{self.portfolio.name} - {self.project.name}"


class PortfolioGoal(models.Model):
    """
    Goals within a portfolio.
    """
    # Relationships
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='goals')
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='portfolios')
    
    # Portfolio goal settings
    priority = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='added_portfolio_goals')
    
    class Meta:
        unique_together = ['portfolio', 'goal']
        ordering = ['priority', '-added_at']
        verbose_name = _('Portfolio Goal')
        verbose_name_plural = _('Portfolio Goals')
    
    def __str__(self):
        return f"{self.portfolio.name} - {self.goal.title}"


class PortfolioMetrics(models.Model):
    """
    Key performance indicators and metrics for portfolios.
    """
    # Metric information
    name = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    unit = models.CharField(max_length=50, blank=True)
    target_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Metric details
    metric_type = models.CharField(max_length=50, choices=[
        ('financial', 'Financial'),
        ('operational', 'Operational'),
        ('quality', 'Quality'),
        ('timeline', 'Timeline'),
        ('resource', 'Resource'),
        ('custom', 'Custom'),
    ])
    
    # Relationships
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='metrics')
    
    # Metadata
    measured_at = models.DateTimeField(auto_now_add=True)
    measured_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='measured_portfolio_metrics')
    
    class Meta:
        ordering = ['-measured_at']
        verbose_name = _('Portfolio Metric')
        verbose_name_plural = _('Portfolio Metrics')
    
    def __str__(self):
        return f"{self.portfolio.name} - {self.name}: {self.value}"
    
    def get_performance_percentage(self):
        """Calculate performance against target."""
        if self.target_value and self.value:
            return round((self.value / self.target_value) * 100, 1)
        return None


class PortfolioMember(models.Model):
    """
    Members with access to portfolio.
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    ]
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolio_memberships')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    
    # Permissions
    can_edit_portfolio = models.BooleanField(default=False)
    can_manage_projects = models.BooleanField(default=False)
    can_manage_goals = models.BooleanField(default=False)
    can_view_analytics = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'portfolio']
        ordering = ['portfolio', 'role', 'user__username']
        verbose_name = _('Portfolio Member')
        verbose_name_plural = _('Portfolio Members')
    
    def __str__(self):
        return f"{self.user.username} - {self.portfolio.name} ({self.role})"
    
    def save(self, *args, **kwargs):
        """Set permissions based on role when saving."""
        if self.role == 'owner':
            self.can_edit_portfolio = True
            self.can_manage_projects = True
            self.can_manage_goals = True
            self.can_view_analytics = True
        elif self.role == 'admin':
            self.can_edit_portfolio = True
            self.can_manage_projects = True
            self.can_manage_goals = True
            self.can_view_analytics = True
        elif self.role == 'member':
            self.can_edit_portfolio = False
            self.can_manage_projects = False
            self.can_manage_goals = False
            self.can_view_analytics = True
        elif self.role == 'viewer':
            self.can_edit_portfolio = False
            self.can_manage_projects = False
            self.can_manage_goals = False
            self.can_view_analytics = False
        
        super().save(*args, **kwargs)


class PortfolioReport(models.Model):
    """
    Generated reports for portfolios.
    """
    REPORT_TYPES = [
        ('summary', 'Summary'),
        ('detailed', 'Detailed'),
        ('financial', 'Financial'),
        ('timeline', 'Timeline'),
        ('resource', 'Resource'),
        ('custom', 'Custom'),
    ]
    
    # Report information
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, default='summary')
    content = models.JSONField(default=dict)
    
    # Report settings
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=50, blank=True)
    
    # Relationships
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='reports')
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_portfolio_reports')
    
    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-generated_at']
        verbose_name = _('Portfolio Report')
        verbose_name_plural = _('Portfolio Reports')
    
    def __str__(self):
        return f"{self.portfolio.name} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('portfolios:report_detail', kwargs={'pk': self.pk})
