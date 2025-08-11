"""
Views for projects app.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Project, ProjectSection, ProjectMember


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 20


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'projects/project_form.html'
    fields = ['name', 'description', 'status', 'priority', 'start_date', 'due_date', 'team']
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.pk})


class ProjectEditView(LoginRequiredMixin, UpdateView):
    model = Project
    template_name = 'projects/project_form.html'
    fields = ['name', 'description', 'status', 'priority', 'start_date', 'due_date', 'team']
    
    def get_success_url(self):
        return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.pk})


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects:project_list')


class ProjectBoardView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_board.html'
    context_object_name = 'project'


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 20


class ProjectSectionsView(LoginRequiredMixin, ListView):
    model = ProjectSection
    template_name = 'projects/project_sections.html'
    context_object_name = 'sections'
    
    def get_queryset(self):
        return ProjectSection.objects.filter(project_id=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = Project.objects.get(pk=self.kwargs['pk'])
        return context


class SectionCreateView(LoginRequiredMixin, CreateView):
    model = ProjectSection
    template_name = 'projects/section_form.html'
    fields = ['name', 'description', 'order']
    
    def form_valid(self, form):
        form.instance.project_id = self.kwargs['pk']
        return super().form_valid(form)


class SectionEditView(LoginRequiredMixin, UpdateView):
    model = ProjectSection
    template_name = 'projects/section_form.html'
    fields = ['name', 'description', 'order']


class SectionDeleteView(LoginRequiredMixin, DeleteView):
    model = ProjectSection
    template_name = 'projects/section_confirm_delete.html'
    success_url = reverse_lazy('projects:project_list')


class ProjectMembersView(LoginRequiredMixin, ListView):
    model = ProjectMember
    template_name = 'projects/project_members.html'
    context_object_name = 'memberships'
    
    def get_queryset(self):
        return ProjectMember.objects.filter(project_id=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = Project.objects.get(pk=self.kwargs['pk'])
        return context


class ProjectMemberAddView(LoginRequiredMixin, CreateView):
    model = ProjectMember
    template_name = 'projects/member_form.html'
    fields = ['user', 'role']
    
    def form_valid(self, form):
        form.instance.project_id = self.kwargs['pk']
        return super().form_valid(form)


class ProjectMemberEditView(LoginRequiredMixin, UpdateView):
    model = ProjectMember
    template_name = 'projects/member_form.html'
    fields = ['user', 'role']


class ProjectMemberRemoveView(LoginRequiredMixin, DeleteView):
    model = ProjectMember
    template_name = 'projects/member_confirm_delete.html'
    success_url = reverse_lazy('projects:project_list')


class ProjectCalendarView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_calendar.html'
    context_object_name = 'project'


class ProjectTimelineView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_timeline.html'
    context_object_name = 'project'


class ProjectTemplateListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/template_list.html'
    context_object_name = 'templates'
    
    def get_queryset(self):
        return Project.objects.filter(is_template=True)


class ProjectTemplateCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'projects/template_form.html'
    fields = ['name', 'description', 'status', 'priority', 'start_date', 'due_date', 'team']
    
    def form_valid(self, form):
        form.instance.is_template = True
        return super().form_valid(form)


class ProjectTemplateDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/template_detail.html'
    context_object_name = 'template'
    
    def get_queryset(self):
        return Project.objects.filter(is_template=True)


class ProjectTemplateEditView(LoginRequiredMixin, UpdateView):
    model = Project
    template_name = 'projects/template_form.html'
    fields = ['name', 'description', 'status', 'priority', 'start_date', 'due_date', 'team']
    
    def get_queryset(self):
        return Project.objects.filter(is_template=True)


class ProjectTemplateDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'projects/template_confirm_delete.html'
    success_url = reverse_lazy('projects:template_list')
    
    def get_queryset(self):
        return Project.objects.filter(is_template=True)


class ProjectCategoryListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        # For now, return empty queryset since we don't have categories yet
        return Project.objects.none()


class ProjectCategoryCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'projects/category_form.html'
    fields = ['name', 'description']
    
    def form_valid(self, form):
        # For now, just create a regular project
        return super().form_valid(form)


class ProjectCategoryEditView(LoginRequiredMixin, UpdateView):
    model = Project
    template_name = 'projects/category_form.html'
    fields = ['name', 'description']


class ProjectCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'projects/category_confirm_delete.html'
    success_url = reverse_lazy('projects:category_list')
