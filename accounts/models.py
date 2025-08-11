"""
User management models for Inspora platform.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.urls import reverse


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    """
    # Basic profile fields
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)

    # Professional fields
    job_title = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(max_length=50, blank=True, unique=True)

    # Preferences
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['username']

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('accounts:user_detail', kwargs={'pk': self.pk})

    def get_full_name_or_username(self):
        """Return full name if available, otherwise username."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username


class Team(models.Model):
    """
    Team model for organizing users into groups.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='team_logos/', null=True, blank=True)
    
    # Team settings
    is_public = models.BooleanField(default=False)
    allow_guest_access = models.BooleanField(default=False)
    max_members = models.PositiveIntegerField(default=100)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_teams')
    
    class Meta:
        ordering = ['name']
        verbose_name = _('Team')
        verbose_name_plural = _('Teams')
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('accounts:team_detail', kwargs={'pk': self.pk})
    
    def get_member_count(self):
        """Return the number of active members in the team."""
        return self.members.filter(is_active=True).count()


class TeamMembership(models.Model):
    """
    Model for managing team memberships with roles and permissions.
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('guest', 'Guest'),
        ('viewer', 'Viewer'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    
    # Permissions
    can_manage_team = models.BooleanField(default=False)
    can_manage_projects = models.BooleanField(default=False)
    can_manage_members = models.BooleanField(default=False)
    can_view_analytics = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'team']
        ordering = ['team', 'role', 'user__username']
        verbose_name = _('Team Membership')
        verbose_name_plural = _('Team Memberships')
    
    def __str__(self):
        return f"{self.user.username} - {self.team.name} ({self.role})"
    
    def save(self, *args, **kwargs):
        # Set permissions based on role
        if self.role == 'owner':
            self.can_manage_team = True
            self.can_manage_projects = True
            self.can_manage_members = True
            self.can_view_analytics = True
        elif self.role == 'admin':
            self.can_manage_projects = True
            self.can_manage_members = True
            self.can_view_analytics = True
        elif self.role == 'member':
            self.can_view_analytics = True
        
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """
    Extended user profile information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal information
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ])
    
    # Address
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Social media
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    
    # Work preferences
    work_schedule = models.CharField(max_length=50, blank=True)
    preferred_communication = models.CharField(max_length=50, blank=True, choices=[
        ('email', 'Email'),
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
        ('phone', 'Phone'),
        ('in_person', 'In Person'),
    ])
    
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
    
    def __str__(self):
        return f"Profile for {self.user.username}"
    
    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'pk': self.pk})


class UserSession(models.Model):
    """Track user sessions for analytics."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-last_activity']

    def __str__(self):
        return f"{self.user.username} - {self.session_key}"


class AIChat(models.Model):
    """AI chat conversations for user support."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_chats')
    session_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"AI Chat - {self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class AIChatMessage(models.Model):
    """Individual messages in AI chat conversations."""
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('ai', 'AI Response'),
        ('system', 'System Message'),
    ]
    
    chat = models.ForeignKey(AIChat, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)  # Store AI response metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.get_message_type_display()} - {self.content[:50]}..."


class AISuggestion(models.Model):
    """AI-generated suggestions for users."""
    SUGGESTION_TYPES = [
        ('task_optimization', 'Task Optimization'),
        ('workflow_improvement', 'Workflow Improvement'),
        ('project_management', 'Project Management'),
        ('team_collaboration', 'Team Collaboration'),
        ('productivity_tip', 'Productivity Tip'),
        ('feature_recommendation', 'Feature Recommendation'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_suggestions')
    suggestion_type = models.CharField(max_length=30, choices=SUGGESTION_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    action_url = models.CharField(max_length=500, blank=True)
    action_text = models.CharField(max_length=100, blank=True)
    priority = models.PositiveIntegerField(default=1)  # 1-5, higher is more important
    is_read = models.BooleanField(default=False)
    is_applied = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return f"{self.get_suggestion_type_display()} - {self.title}"


class AIWorkflowAssistant(models.Model):
    """AI-powered workflow assistance and automation."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_workflows')
    workflow_type = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    description = models.TextField()
    configuration = models.JSONField(default=dict)  # Workflow configuration
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_executed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.workflow_type} - {self.name}"


class AIKnowledgeBase(models.Model):
    """AI knowledge base for contextual help."""
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=100)
    tags = models.JSONField(default=list, blank=True)
    search_keywords = models.JSONField(default=list, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-usage_count', '-last_updated']
        verbose_name_plural = 'AI Knowledge Base'
    
    def __str__(self):
        return self.title
