"""
Views for tasks app.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Task, TaskComment, TaskAttachment


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 20


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'tasks/task_form.html'
    fields = ['title', 'description', 'status', 'priority', 'project', 'section', 'assignee', 'start_date', 'due_date', 'estimated_hours']
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('tasks:task_detail', kwargs={'pk': self.object.pk})


class TaskEditView(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = 'tasks/task_form.html'
    fields = ['title', 'description', 'status', 'priority', 'project', 'section', 'assignee', 'start_date', 'due_date', 'estimated_hours']
    
    def get_success_url(self):
        return reverse_lazy('tasks:task_detail', kwargs={'pk': self.object.pk})


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:task_list')


class TaskBoardView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_board.html'
    context_object_name = 'tasks'


class TaskCalendarView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_calendar.html'
    context_object_name = 'tasks'


class TaskTimelineView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_timeline.html'
    context_object_name = 'tasks'


class MyTasksView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/my_tasks.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)


class OverdueTasksView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/overdue_tasks.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        from django.utils import timezone
        return Task.objects.filter(due_date__lt=timezone.now().date(), status__in=['todo', 'in_progress'])


class TaskStartView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['status']
    template_name = 'tasks/task_start.html'
    
    def form_valid(self, form):
        form.instance.status = 'in_progress'
        form.instance.start_date = timezone.now()
        return super().form_valid(form)


class TaskCompleteView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['status', 'progress']
    template_name = 'tasks/task_complete.html'
    
    def form_valid(self, form):
        form.instance.status = 'completed'
        form.instance.progress = 100
        form.instance.completed_date = timezone.now()
        return super().form_valid(form)


class TaskAssignView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['assignee']
    template_name = 'tasks/task_assign.html'


class TaskMoveView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['section']
    template_name = 'tasks/task_move.html'


class SubtaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/subtask_list.html'
    context_object_name = 'subtasks'
    
    def get_queryset(self):
        return Task.objects.filter(parent_task_id=self.kwargs['pk'])


class SubtaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'tasks/subtask_form.html'
    fields = ['title', 'description', 'status', 'priority', 'assignee', 'start_date', 'due_date', 'estimated_hours']
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.is_subtask = True
        form.instance.parent_task_id = self.kwargs['pk']
        return super().form_valid(form)


class SubtaskEditView(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = 'tasks/subtask_form.html'
    fields = ['title', 'description', 'status', 'priority', 'assignee', 'start_date', 'due_date', 'estimated_hours']


class SubtaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/subtask_confirm_delete.html'
    success_url = reverse_lazy('tasks:task_list')


class TaskDependenciesView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_dependencies.html'
    context_object_name = 'dependencies'
    
    def get_queryset(self):
        # For now, return empty queryset since we don't have dependencies yet
        return Task.objects.none()


class DependencyAddView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'tasks/dependency_form.html'
    fields = ['title', 'description', 'status', 'priority', 'assignee', 'start_date', 'due_date']
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class DependencyEditView(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = 'tasks/dependency_form.html'
    fields = ['title', 'description', 'status', 'priority', 'assignee', 'start_date', 'due_date']


class DependencyDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/dependency_confirm_delete.html'
    success_url = reverse_lazy('tasks:task_list')


class TaskCommentsView(LoginRequiredMixin, ListView):
    model = TaskComment
    template_name = 'tasks/task_comments.html'
    context_object_name = 'comments'
    
    def get_queryset(self):
        return TaskComment.objects.filter(task_id=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task'] = Task.objects.get(pk=self.kwargs['pk'])
        return context


class CommentAddView(LoginRequiredMixin, CreateView):
    model = TaskComment
    template_name = 'tasks/comment_form.html'
    fields = ['content']
    
    def form_valid(self, form):
        form.instance.task_id = self.kwargs['pk']
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentEditView(LoginRequiredMixin, UpdateView):
    model = TaskComment
    template_name = 'tasks/comment_form.html'
    fields = ['content']


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = TaskComment
    template_name = 'tasks/comment_confirm_delete.html'
    success_url = reverse_lazy('tasks:task_list')


class TaskAttachmentsView(LoginRequiredMixin, ListView):
    model = TaskAttachment
    template_name = 'tasks/task_attachments.html'
    context_object_name = 'attachments'
    
    def get_queryset(self):
        return TaskAttachment.objects.filter(task_id=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task'] = Task.objects.get(pk=self.kwargs['pk'])
        return context


class AttachmentUploadView(LoginRequiredMixin, CreateView):
    model = TaskAttachment
    template_name = 'tasks/attachment_form.html'
    fields = ['file', 'description']
    
    def form_valid(self, form):
        form.instance.task_id = self.kwargs['pk']
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)


class AttachmentDownloadView(LoginRequiredMixin, DetailView):
    model = TaskAttachment
    template_name = 'tasks/attachment_download.html'


class AttachmentDeleteView(LoginRequiredMixin, DeleteView):
    model = TaskAttachment
    template_name = 'tasks/attachment_confirm_delete.html'
    success_url = reverse_lazy('tasks:task_list')


class TaskTemplateListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/template_list.html'
    context_object_name = 'templates'
    
    def get_queryset(self):
        # For now, return empty queryset since we don't have templates yet
        return Task.objects.none()


class TaskTemplateCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'tasks/template_form.html'
    fields = ['title', 'description', 'status', 'priority', 'project', 'section', 'assignee', 'start_date', 'due_date', 'estimated_hours']
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.is_template = True
        return super().form_valid(form)


class TaskTemplateDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/template_detail.html'
    context_object_name = 'template'


class TaskTemplateEditView(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = 'tasks/template_form.html'
    fields = ['title', 'description', 'status', 'priority', 'project', 'section', 'assignee', 'start_date', 'due_date', 'estimated_hours']


class TaskTemplateDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/template_confirm_delete.html'
    success_url = reverse_lazy('tasks:template_list')


class TaskTimeView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_time.html'
    context_object_name = 'task'


class TimeStartView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['status']
    template_name = 'tasks/time_start.html'
    
    def form_valid(self, form):
        form.instance.status = 'in_progress'
        form.instance.start_date = timezone.now()
        return super().form_valid(form)


class TimeStopView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['status', 'progress']
    template_name = 'tasks/time_stop.html'
    
    def form_valid(self, form):
        form.instance.status = 'completed'
        form.instance.progress = 100
        form.instance.completed_date = timezone.now()
        return super().form_valid(form)


class TimeLogsView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/time_logs.html'
    context_object_name = 'logs'
    
    def get_queryset(self):
        # For now, return empty queryset since we don't have time logs yet
        return Task.objects.none()
