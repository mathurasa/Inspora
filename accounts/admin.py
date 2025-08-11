"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Team, TeamMembership, UserProfile, UserSession, AIChat, AIChatMessage, AISuggestion, AIWorkflowAssistant, AIKnowledgeBase


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'job_title', 'department', 'is_active', 'is_verified']
    list_filter = ['is_active', 'is_verified', 'department', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'job_title']
    ordering = ['username']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': ('avatar', 'bio', 'phone_number', 'job_title', 'department', 'employee_id')
        }),
        ('Preferences', {
            'fields': ('timezone', 'language', 'email_notifications', 'push_notifications')
        }),
        ('Status', {
            'fields': ('is_verified', 'last_activity')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Profile Information', {
            'fields': ('job_title', 'department', 'employee_id')
        }),
    )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_public', 'max_members', 'created_by', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'description', 'created_by__username']
    list_editable = ['is_public', 'max_members']


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'team', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'team', 'joined_at']
    search_fields = ['user__username', 'team__name']
    list_editable = ['role', 'is_active']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'city', 'country', 'work_schedule']
    list_filter = ['gender', 'country', 'work_schedule']
    search_fields = ['user__username', 'city', 'country']


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'created_at', 'last_activity', 'is_active']
    list_filter = ['is_active', 'created_at', 'last_activity']
    search_fields = ['user__username', 'ip_address']
    date_hierarchy = 'created_at'


@admin.register(AIChat)
class AIChatAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_id', 'title', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'session_id', 'title']
    ordering = ['-updated_at']


@admin.register(AIChatMessage)
class AIChatMessageAdmin(admin.ModelAdmin):
    list_display = ['chat', 'message_type', 'content_preview', 'created_at']
    list_filter = ['message_type', 'created_at']
    search_fields = ['chat__user__username', 'content']
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(AISuggestion)
class AISuggestionAdmin(admin.ModelAdmin):
    list_display = ['user', 'suggestion_type', 'title', 'priority', 'is_read', 'is_applied', 'is_active', 'created_at']
    list_filter = ['suggestion_type', 'priority', 'is_read', 'is_applied', 'is_active', 'created_at']
    search_fields = ['user__username', 'title', 'description']
    ordering = ['-priority', '-created_at']


@admin.register(AIWorkflowAssistant)
class AIWorkflowAssistantAdmin(admin.ModelAdmin):
    list_display = ['user', 'workflow_type', 'name', 'is_active', 'created_at', 'last_executed']
    list_filter = ['workflow_type', 'is_active', 'created_at']
    search_fields = ['user__username', 'name', 'description']
    ordering = ['-created_at']


@admin.register(AIKnowledgeBase)
class AIKnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'usage_count', 'is_active', 'last_updated']
    list_filter = ['category', 'is_active', 'last_updated']
    search_fields = ['title', 'content', 'tags']
    ordering = ['-usage_count', '-last_updated']
