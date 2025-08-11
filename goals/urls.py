from django.urls import path
from . import views

app_name = 'goals'

urlpatterns = [
    # Goal management
    path('', views.GoalListView.as_view(), name='goal_list'),
    path('create/', views.GoalCreateView.as_view(), name='goal_create'),
    path('<int:pk>/', views.GoalDetailView.as_view(), name='goal_detail'),
    path('<int:pk>/edit/', views.GoalEditView.as_view(), name='goal_edit'),
    path('<int:pk>/delete/', views.GoalDeleteView.as_view(), name='goal_delete'),
    
    # Goal views
    path('my-goals/', views.MyGoalsView.as_view(), name='my_goals'),
    path('team-goals/', views.TeamGoalsView.as_view(), name='team_goals'),
    path('company-goals/', views.CompanyGoalsView.as_view(), name='company_goals'),
    path('overdue/', views.OverdueGoalsView.as_view(), name='overdue_goals'),
    
    # Goal progress
    path('<int:pk>/progress/', views.GoalProgressView.as_view(), name='goal_progress'),
    path('<int:pk>/progress/update/', views.ProgressUpdateView.as_view(), name='progress_update'),
    path('<int:pk>/progress/history/', views.ProgressHistoryView.as_view(), name='progress_history'),
    
    # Goal alignment
    path('<int:pk>/alignment/', views.GoalAlignmentView.as_view(), name='goal_alignment'),
    path('<int:pk>/alignment/add/', views.AlignmentAddView.as_view(), name='alignment_add'),
    path('alignment/<int:pk>/edit/', views.AlignmentEditView.as_view(), name='alignment_edit'),
    path('alignment/<int:pk>/delete/', views.AlignmentDeleteView.as_view(), name='alignment_delete'),
    
    # Goal comments
    path('<int:pk>/comments/', views.GoalCommentsView.as_view(), name='goal_comments'),
    path('<int:pk>/comments/add/', views.CommentAddView.as_view(), name='comment_add'),
    path('comments/<int:pk>/edit/', views.CommentEditView.as_view(), name='comment_edit'),
    path('comments/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
    
    # Goal templates
    path('templates/', views.GoalTemplateListView.as_view(), name='template_list'),
    path('templates/create/', views.GoalTemplateCreateView.as_view(), name='template_create'),
    path('templates/<int:pk>/', views.GoalTemplateDetailView.as_view(), name='template_detail'),
    path('templates/<int:pk>/edit/', views.GoalTemplateEditView.as_view(), name='template_edit'),
    path('templates/<int:pk>/delete/', views.GoalTemplateDeleteView.as_view(), name='template_delete'),
]
