"""
Admin configuration for projects app.
"""
from django.contrib import admin
from .models import Project, ProjectSection, ProjectMember


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'priority', 'owner', 'team', 'progress', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'team', 'created_at', 'due_date']
    search_fields = ['name', 'description', 'owner__username', 'team__name']
    list_editable = ['status', 'priority', 'progress']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'status', 'priority')
        }),
        ('Dates & Progress', {
            'fields': ('start_date', 'due_date', 'completed_date', 'progress')
        }),
        ('Ownership & Team', {
            'fields': ('owner', 'team')
        }),
        ('Metadata', {
            'fields': ('tags', 'custom_fields')
        }),
    )


@admin.register(ProjectSection)
class ProjectSectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'order', 'description']
    list_filter = ['project']
    search_fields = ['name', 'project__name']
    list_editable = ['order']


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'project', 'joined_at']
    search_fields = ['user__username', 'project__name']
    list_editable = ['role', 'is_active']
