from django.contrib import admin
from .models import Integration, GoogleDriveIntegration, IntegrationLog, IntegrationWebhook


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ['name', 'integration_type', 'status', 'created_by', 'created_at', 'last_sync']
    list_filter = ['integration_type', 'status', 'is_active', 'created_at']
    search_fields = ['name', 'created_by__username', 'created_by__email']
    readonly_fields = ['created_at', 'updated_at', 'last_sync']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'integration_type', 'status', 'is_active')
        }),
        ('Configuration', {
            'fields': ('config', 'credentials')
        }),
        ('Settings', {
            'fields': ('auto_sync', 'sync_interval')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at', 'last_sync'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GoogleDriveIntegration)
class GoogleDriveIntegrationAdmin(admin.ModelAdmin):
    list_display = ['integration', 'can_read', 'can_write', 'can_share', 'token_expiry']
    list_filter = ['can_read', 'can_write', 'can_share']
    readonly_fields = ['integration']
    
    fieldsets = (
        ('Integration', {
            'fields': ('integration',)
        }),
        ('Google OAuth2', {
            'fields': ('access_token', 'refresh_token', 'token_expiry')
        }),
        ('Drive Settings', {
            'fields': ('root_folder_id', 'sync_folders')
        }),
        ('Permissions', {
            'fields': ('can_read', 'can_write', 'can_share')
        }),
    )


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    list_display = ['integration', 'level', 'message', 'timestamp']
    list_filter = ['level', 'timestamp', 'integration__integration_type']
    search_fields = ['message', 'integration__name']
    readonly_fields = ['timestamp']
    
    fieldsets = (
        ('Log Information', {
            'fields': ('integration', 'level', 'message', 'timestamp')
        }),
        ('Details', {
            'fields': ('details',),
            'classes': ('collapse',)
        }),
    )


@admin.register(IntegrationWebhook)
class IntegrationWebhookAdmin(admin.ModelAdmin):
    list_display = ['name', 'integration', 'url', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'integration__integration_type']
    search_fields = ['name', 'url', 'integration__name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Webhook Information', {
            'fields': ('name', 'integration', 'url', 'is_active')
        }),
        ('Configuration', {
            'fields': ('events', 'headers')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
