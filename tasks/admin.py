"""
Admin configuration for tasks app.
"""
from django.contrib import admin
from .models import Task, TaskComment, TaskAttachment


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
            'fields': ('progress', 'estimated_hours', 'actual_hours')
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
