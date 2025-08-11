from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # Project management
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('<int:pk>/edit/', views.ProjectEditView.as_view(), name='project_edit'),
    path('<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    
    # Project views
    path('<int:pk>/board/', views.ProjectBoardView.as_view(), name='project_board'),
    path('<int:pk>/list/', views.ProjectListView.as_view(), name='project_list_view'),
    path('<int:pk>/calendar/', views.ProjectCalendarView.as_view(), name='project_calendar'),
    path('<int:pk>/timeline/', views.ProjectTimelineView.as_view(), name='project_timeline'),
    
    # Project sections
    path('<int:pk>/sections/', views.ProjectSectionsView.as_view(), name='project_sections'),
    path('<int:pk>/sections/create/', views.SectionCreateView.as_view(), name='section_create'),
    path('sections/<int:pk>/edit/', views.SectionEditView.as_view(), name='section_edit'),
    path('sections/<int:pk>/delete/', views.SectionDeleteView.as_view(), name='section_delete'),
    
    # Project members
    path('<int:pk>/members/', views.ProjectMembersView.as_view(), name='project_members'),
    path('<int:pk>/members/add/', views.ProjectMemberAddView.as_view(), name='member_add'),
    path('members/<int:pk>/edit/', views.ProjectMemberEditView.as_view(), name='member_edit'),
    path('members/<int:pk>/remove/', views.ProjectMemberRemoveView.as_view(), name='member_remove'),
    
    # Project templates
    path('templates/', views.ProjectTemplateListView.as_view(), name='template_list'),
    path('templates/create/', views.ProjectTemplateCreateView.as_view(), name='template_create'),
    path('templates/<int:pk>/', views.ProjectTemplateDetailView.as_view(), name='template_detail'),
    path('templates/<int:pk>/edit/', views.ProjectTemplateEditView.as_view(), name='template_edit'),
    path('templates/<int:pk>/delete/', views.ProjectTemplateDeleteView.as_view(), name='template_delete'),
    
    # Project categories
    path('categories/', views.ProjectCategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.ProjectCategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.ProjectCategoryEditView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.ProjectCategoryDeleteView.as_view(), name='category_delete'),
]
