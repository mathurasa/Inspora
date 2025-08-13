from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # User management
    path('', views.user_dashboard, name='dashboard'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/edit/', views.UserProfileEditView.as_view(), name='profile_edit'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    
    # Team management
    path('teams/', views.TeamListView.as_view(), name='team_list'),
    path('teams/create/', views.TeamCreateView.as_view(), name='team_create'),
    path('teams/<int:pk>/', views.TeamDetailView.as_view(), name='team_detail'),
    path('teams/<int:pk>/edit/', views.TeamEditView.as_view(), name='team_edit'),
    path('teams/<int:pk>/members/', views.TeamMembersView.as_view(), name='team_members'),
    
    # Authentication (if not using Django's built-in)
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('logout/confirm/', views.logout_confirm, name='logout_confirm'),
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # Static pages
    path('pricing/', views.pricing_view, name='pricing'),
    path('resources/', views.resources_view, name='resources'),
    path('resources/help/', views.help_center_view, name='help_center'),
    path('resources/academy/', views.academy_view, name='academy'),
    path('resources/certifications/', views.certifications_view, name='certifications'),
    path('resources/forums/', views.forums_view, name='forums'),
    path('resources/work-management/', views.work_management_view, name='work_management'),
    path('resources/customer-stories/', views.customer_stories_view, name='customer_stories'),
    path('resources/events/', views.events_view, name='events'),
    path('resources/support/', views.support_view, name='support'),
    path('resources/developer/', views.developer_view, name='developer'),
    path('resources/partners/', views.partners_view, name='partners'),
    path('contact/', views.contact_view, name='contact'),
    path('resources/templates/', views.templates_view, name='templates'),
    path('resources/templates/projects/', views.project_templates_view, name='project_templates'),
    path('resources/templates/goals/', views.goal_templates_view, name='goal_templates'),
    path('resources/templates/meetings/', views.meeting_templates_view, name='meeting_templates'),
    
    # AI Features
    path('ai/chat/', views.ai_chat_view, name='ai_chat'),
    path('ai/suggestions/', views.ai_suggestions_view, name='ai_suggestions'),
    path('ai/workflow/', views.ai_workflow_view, name='ai_workflow'),
    path('ai/knowledge/', views.ai_knowledge_search, name='ai_knowledge'),
    path('api/ai/chat/', views.ai_chat_api, name='ai_chat_api'),
    path('api/ai/suggestions/generate/', views.ai_generate_suggestions, name='ai_generate_suggestions'),
    path('api/ai/suggestions/<int:suggestion_id>/read/', views.ai_mark_suggestion_read, name='ai_mark_suggestion_read'),
    path('api/ai/suggestions/<int:suggestion_id>/applied/', views.ai_mark_suggestion_applied, name='ai_mark_suggestion_applied'),
]
