"""
Admin configuration for tasks app.
"""
from django.contrib import admin
from .models import Task, TaskComment, TaskAttachment, TimeLog, TaskTemplate


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'status', 'priority', 'assignee', 'progress', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'project', 'assignee', 'created_at', 'due_date']
    search_fields = ['title', 'description', 'project__name', 'assignee__username']
    list_editable = ['status', 'priority', 'progress']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'status', 'priority')
        }),
        ('Relationships', {
            'fields': ('project', 'section', 'assignee', 'created_by', 'parent_task')
        }),
        ('Progress & Time', {
            'fields': ('progress', 'estimated_hours', 'actual_hours', 'is_timer_running', 'timer_started_at', 'total_time_spent')
        }),
        ('Dates', {
            'fields': ('due_date', 'start_date', 'completed_date')
        }),
        ('Metadata', {
            'fields': ('tags', 'custom_fields')
        }),
    )


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'author', 'content', 'created_at']
    list_filter = ['created_at', 'author']
    search_fields = ['content', 'task__title', 'author__username']
    date_hierarchy = 'created_at'


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'task', 'uploaded_by', 'file_size', 'file_type', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at', 'task']
    search_fields = ['filename', 'task__title', 'uploaded_by__username']
    date_hierarchy = 'uploaded_at'


@admin.register(TimeLog)
class TimeLogAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'start_time', 'end_time', 'duration', 'is_billable', 'hourly_rate']
    list_filter = ['is_billable', 'start_time', 'user', 'task__project']
    search_fields = ['task__title', 'user__username', 'description']
    date_hierarchy = 'start_time'
    readonly_fields = ['duration']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('task', 'user', 'description')
        }),
        ('Time Tracking', {
            'fields': ('start_time', 'end_time', 'duration')
        }),
        ('Billing', {
            'fields': ('is_billable', 'hourly_rate')
        }),
    )


@admin.register(TaskTemplate)
class TaskTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'priority', 'estimated_hours', 'is_active', 'created_by', 'created_at']
    list_filter = ['category', 'priority', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'category']
    list_editable = ['is_active', 'priority']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'description', 'category', 'priority', 'estimated_hours')
        }),
        ('Configuration', {
            'fields': ('tags', 'custom_fields', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
