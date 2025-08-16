"""
User management models for Inspora platform.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.urls import reverse
from django.utils import timezone


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
    employee_id = models.CharField(max_length=50, blank=True, null=True, unique=True)

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
    
    def save(self, *args, **kwargs):
        """Custom save method to handle employee_id uniqueness."""
        if not self.employee_id:
            self.employee_id = None
        super().save(*args, **kwargs)


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


class SubscriptionPlan(models.Model):
    """
    Subscription plan model for different pricing tiers.
    """
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    
    BILLING_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Pricing
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    yearly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Features
    max_team_members = models.PositiveIntegerField(default=3)
    max_projects = models.PositiveIntegerField(default=2)
    max_storage_gb = models.PositiveIntegerField(default=1)
    
    # Plan features
    features = models.JSONField(default=dict)
    
    # Plan status
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['monthly_price']
        verbose_name = _('Subscription Plan')
        verbose_name_plural = _('Subscription Plans')
    
    def __str__(self):
        return self.display_name
    
    def get_price(self, billing_cycle):
        """Return price for specific billing cycle."""
        return self.yearly_price if billing_cycle == 'yearly' else self.monthly_price
    
    def get_discount_percentage(self):
        """Calculate discount percentage for yearly billing."""
        if self.monthly_price > 0:
            yearly_total = self.monthly_price * 12
            discount = ((yearly_total - self.yearly_price) / yearly_total) * 100
            return round(discount, 1)
        return 0


class PaymentMethod(models.Model):
    """
    Payment method model for storing user payment information.
    """
    PAYMENT_TYPES = [
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
        ('paypal', 'PayPal'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, default='card')
    
    # Card information (encrypted in production)
    card_last4 = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=20, blank=True)  # visa, mastercard, etc.
    card_exp_month = models.PositiveIntegerField(null=True, blank=True)
    card_exp_year = models.PositiveIntegerField(null=True)
    
    # Payment provider IDs
    stripe_payment_method_id = models.CharField(max_length=100, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    
    # Status
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Payment Method')
        verbose_name_plural = _('Payment Methods')
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        if self.payment_type == 'card':
            return f"{self.card_brand.title()} ****{self.card_last4}"
        return f"{self.get_payment_type_display()} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        # Ensure only one default payment method per user
        if self.is_default:
            PaymentMethod.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class UserSubscription(models.Model):
    """
    User subscription model to track user's current plan.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('trial', 'Trial'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('past_due', 'Past Due'),
        ('unpaid', 'Unpaid'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    billing_cycle = models.CharField(max_length=20, choices=SubscriptionPlan.BILLING_CHOICES, default='monthly')
    
    # Subscription details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    trial_end_date = models.DateTimeField(null=True, blank=True)
    next_billing_date = models.DateTimeField(null=True, blank=True)
    
    # Payment details
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    stripe_invoice_id = models.CharField(max_length=100, blank=True)
    
    # Billing amounts
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    next_billing_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('User Subscription')
        verbose_name_plural = _('User Subscriptions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.display_name}"
    
    def is_active(self):
        """Check if subscription is currently active."""
        if self.status == 'active':
            if self.end_date:
                return self.end_date > timezone.now()
            return True
        return False
    
    def is_trial_active(self):
        """Check if trial period is still active."""
        if self.trial_end_date:
            return self.trial_end_date > timezone.now()
        return False
    
    def get_next_billing_amount(self):
        """Get the amount for the next billing cycle."""
        if self.billing_cycle == 'yearly':
            return self.plan.yearly_price
        return self.plan.monthly_price


class UserProfile(models.Model):
    """
    Extended user profile with additional information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Company information
    company_name = models.CharField(max_length=200, blank=True)
    company_size = models.CharField(max_length=50, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    
    # Professional details
    years_experience = models.PositiveIntegerField(default=0)
    skills = models.JSONField(default=list)
    
    # Preferences
    preferred_contact_method = models.CharField(max_length=20, default='email')
    marketing_consent = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
    
    def __str__(self):
        return f"{self.user.username} Profile"


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


class GoogleDriveIntegration(models.Model):
    """
    Google Drive integration for document management.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='google_drive')
    
    # OAuth2 credentials
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_expiry = models.DateTimeField()
    
    # Drive information
    drive_id = models.CharField(max_length=100, blank=True)
    drive_name = models.CharField(max_length=200, blank=True)
    
    # Settings
    auto_sync = models.BooleanField(default=True)
    sync_frequency = models.CharField(max_length=20, choices=[
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('manual', 'Manual Only'),
    ], default='daily')
    
    # Status
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Google Drive Integration')
        verbose_name_plural = _('Google Drive Integrations')
    
    def __str__(self):
        return f"{self.user.username} - Google Drive"
    
    def is_token_expired(self):
        """Check if the access token has expired."""
        from django.utils import timezone
        return timezone.now() > self.token_expiry


class GitHubIntegration(models.Model):
    """
    GitHub integration for repository and file management.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='github')
    
    # OAuth2 credentials
    access_token = models.TextField()
    token_type = models.CharField(max_length=20, default='Bearer')
    
    # GitHub information
    github_username = models.CharField(max_length=100, blank=True)
    github_email = models.EmailField(blank=True)
    
    # Settings
    auto_sync = models.BooleanField(default=True)
    sync_frequency = models.CharField(max_length=20, choices=[
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('manual', 'Manual Only'),
    ], default='daily')
    
    # Repository settings
    default_repo = models.CharField(max_length=200, blank=True)
    sync_private_repos = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('GitHub Integration')
        verbose_name_plural = _('GitHub Integrations')
    
    def __str__(self):
        return f"{self.user.username} - GitHub"


class Document(models.Model):
    """
    Document model for managing files from various sources.
    """
    SOURCE_CHOICES = [
        ('local', 'Local Upload'),
        ('google_drive', 'Google Drive'),
        ('github', 'GitHub'),
        ('dropbox', 'Dropbox'),
        ('onedrive', 'OneDrive'),
    ]
    
    FILE_TYPES = [
        ('document', 'Document'),
        ('spreadsheet', 'Spreadsheet'),
        ('presentation', 'Presentation'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('archive', 'Archive'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # File information
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField(default=0)  # in bytes
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, default='document')
    mime_type = models.CharField(max_length=100, blank=True)
    
    # Source information
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='local')
    source_id = models.CharField(max_length=255, blank=True)  # ID from source system
    source_url = models.URLField(blank=True)
    
    # File storage
    local_file = models.FileField(upload_to='documents/', null=True, blank=True)
    
    # Sharing and permissions
    is_public = models.BooleanField(default=False)
    shared_with = models.ManyToManyField(User, related_name='shared_documents', blank=True)
    
    # Tags and organization
    tags = models.JSONField(default=list)
    folder = models.CharField(max_length=100, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')
    
    def __str__(self):
        return self.title
    
    def get_file_size_display(self):
        """Return human-readable file size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"
    
    def get_download_url(self):
        """Get download URL based on source."""
        if self.source == 'local' and self.local_file:
            return self.local_file.url
        elif self.source_url:
            return self.source_url
        return None
    
    def can_access(self, user):
        """Check if user can access this document."""
        return (self.user == user or 
                self.is_public or 
                user in self.shared_with.all())


class DocumentVersion(models.Model):
    """
    Version history for documents.
    """
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    
    # File information
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    mime_type = models.CharField(max_length=100)
    
    # Storage
    local_file = models.FileField(upload_to='document_versions/', null=True, blank=True)
    source_url = models.URLField(blank=True)
    
    # Change information
    change_description = models.TextField(blank=True)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-version_number']
        unique_together = ['document', 'version_number']
        verbose_name = _('Document Version')
        verbose_name_plural = _('Document Versions')
    
    def __str__(self):
        return f"{self.document.title} v{self.version_number}"
