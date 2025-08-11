from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Task management
    path('', views.TaskListView.as_view(), name='task_list'),
    path('create/', views.TaskCreateView.as_view(), name='task_create'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('<int:pk>/edit/', views.TaskEditView.as_view(), name='task_edit'),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    
    # Task views
    path('board/', views.TaskBoardView.as_view(), name='task_board'),
    path('calendar/', views.TaskCalendarView.as_view(), name='task_calendar'),
    path('timeline/', views.TaskTimelineView.as_view(), name='task_timeline'),
    path('my-tasks/', views.MyTasksView.as_view(), name='my_tasks'),
    path('overdue/', views.OverdueTasksView.as_view(), name='overdue_tasks'),
    
    # Task actions
    path('<int:pk>/start/', views.TaskStartView.as_view(), name='task_start'),
    path('<int:pk>/complete/', views.TaskCompleteView.as_view(), name='task_complete'),
    path('<int:pk>/assign/', views.TaskAssignView.as_view(), name='task_assign'),
    path('<int:pk>/move/', views.TaskMoveView.as_view(), name='task_move'),
    
    # Subtasks
    path('<int:pk>/subtasks/', views.SubtaskListView.as_view(), name='subtask_list'),
    path('<int:pk>/subtasks/create/', views.SubtaskCreateView.as_view(), name='subtask_create'),
    path('subtasks/<int:pk>/edit/', views.SubtaskEditView.as_view(), name='subtask_edit'),
    path('subtasks/<int:pk>/delete/', views.SubtaskDeleteView.as_view(), name='subtask_delete'),
    
    # Task dependencies
    path('<int:pk>/dependencies/', views.TaskDependenciesView.as_view(), name='task_dependencies'),
    path('<int:pk>/dependencies/add/', views.DependencyAddView.as_view(), name='dependency_add'),
    path('dependencies/<int:pk>/edit/', views.DependencyEditView.as_view(), name='dependency_edit'),
    path('dependencies/<int:pk>/delete/', views.DependencyDeleteView.as_view(), name='dependency_delete'),
    
    # Task comments
    path('<int:pk>/comments/', views.TaskCommentsView.as_view(), name='task_comments'),
    path('<int:pk>/comments/add/', views.CommentAddView.as_view(), name='comment_add'),
    path('comments/<int:pk>/edit/', views.CommentEditView.as_view(), name='comment_edit'),
    path('comments/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
    
    # Task attachments
    path('<int:pk>/attachments/', views.TaskAttachmentsView.as_view(), name='task_attachments'),
    path('<int:pk>/attachments/upload/', views.AttachmentUploadView.as_view(), name='attachment_upload'),
    path('attachments/<int:pk>/download/', views.AttachmentDownloadView.as_view(), name='attachment_download'),
    path('attachments/<int:pk>/delete/', views.AttachmentDeleteView.as_view(), name='attachment_delete'),
    
    # Task templates
    path('templates/', views.TaskTemplateListView.as_view(), name='template_list'),
    path('templates/create/', views.TaskTemplateCreateView.as_view(), name='template_create'),
    path('templates/<int:pk>/', views.TaskTemplateDetailView.as_view(), name='template_detail'),
    path('templates/<int:pk>/edit/', views.TaskTemplateEditView.as_view(), name='template_edit'),
    path('templates/<int:pk>/delete/', views.TaskTemplateDeleteView.as_view(), name='template_delete'),
    
    # Time tracking
    path('<int:pk>/time/', views.TaskTimeView.as_view(), name='task_time'),
    path('<int:pk>/time/start/', views.TimeStartView.as_view(), name='time_start'),
    path('<int:pk>/time/stop/', views.TimeStopView.as_view(), name='time_stop'),
    path('<int:pk>/time/logs/', views.TimeLogsView.as_view(), name='time_logs'),
]
