from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Goal, GoalTemplate

class GoalListView(LoginRequiredMixin, ListView):
    model = Goal
    template_name = 'goals/goal_list.html'
    context_object_name = 'goals'
    paginate_by = 20

class GoalCreateView(LoginRequiredMixin, CreateView):
    model = Goal
    template_name = 'goals/goal_form.html'
    fields = ['title', 'description', 'target_date', 'priority', 'status']
    success_url = reverse_lazy('goals:goal_list')

class GoalDetailView(LoginRequiredMixin, DetailView):
    model = Goal
    template_name = 'goals/goal_detail.html'
    context_object_name = 'goal'

class GoalEditView(LoginRequiredMixin, UpdateView):
    model = Goal
    template_name = 'goals/goal_form.html'
    fields = ['title', 'description', 'target_date', 'priority', 'status']
    success_url = reverse_lazy('goals:goal_list')

class GoalDeleteView(LoginRequiredMixin, DeleteView):
    model = Goal
    template_name = 'goals/goal_confirm_delete.html'
    success_url = reverse_lazy('goals:goal_list')

class MyGoalsView(LoginRequiredMixin, ListView):
    model = Goal
    template_name = 'goals/my_goals.html'
    context_object_name = 'goals'
    paginate_by = 20

    def get_queryset(self):
        return Goal.objects.filter(assigned_to=self.request.user)

class TeamGoalsView(LoginRequiredMixin, ListView):
    model = Goal
    template_name = 'goals/team_goals.html'
    context_object_name = 'goals'
    paginate_by = 20

class CompanyGoalsView(LoginRequiredMixin, ListView):
    model = Goal
    template_name = 'goals/company_goals.html'
    context_object_name = 'goals'
    paginate_by = 20

class OverdueGoalsView(LoginRequiredMixin, ListView):
    model = Goal
    template_name = 'goals/overdue_goals.html'
    context_object_name = 'goals'
    paginate_by = 20

class GoalProgressView(LoginRequiredMixin, DetailView):
    model = Goal
    template_name = 'goals/goal_progress.html'
    context_object_name = 'goal'

class ProgressUpdateView(LoginRequiredMixin, UpdateView):
    model = Goal
    template_name = 'goals/progress_update.html'
    fields = ['progress_percentage', 'progress_notes']
    success_url = reverse_lazy('goals:goal_list')

class ProgressHistoryView(LoginRequiredMixin, DetailView):
    model = Goal
    template_name = 'goals/progress_history.html'
    context_object_name = 'goal'

class GoalAlignmentView(LoginRequiredMixin, DetailView):
    model = Goal
    template_name = 'goals/goal_alignment.html'
    context_object_name = 'goal'

class AlignmentAddView(LoginRequiredMixin, CreateView):
    model = Goal
    template_name = 'goals/alignment_form.html'
    fields = ['title', 'description']
    success_url = reverse_lazy('goals:goal_list')

class AlignmentEditView(LoginRequiredMixin, UpdateView):
    model = Goal
    template_name = 'goals/alignment_form.html'
    fields = ['title', 'description']
    success_url = reverse_lazy('goals:goal_list')

class AlignmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Goal
    template_name = 'goals/alignment_confirm_delete.html'
    success_url = reverse_lazy('goals:goal_list')

class GoalCommentsView(LoginRequiredMixin, DetailView):
    model = Goal
    template_name = 'goals/goal_comments.html'
    context_object_name = 'goal'

class CommentAddView(LoginRequiredMixin, CreateView):
    model = Goal
    template_name = 'goals/comment_form.html'
    fields = ['title', 'content']
    success_url = reverse_lazy('goals:goal_list')

class CommentEditView(LoginRequiredMixin, UpdateView):
    model = Goal
    template_name = 'goals/comment_form.html'
    fields = ['title', 'content']
    success_url = reverse_lazy('goals:goal_list')

class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Goal
    template_name = 'goals/comment_confirm_delete.html'
    success_url = reverse_lazy('goals:goal_list')

class GoalTemplateListView(LoginRequiredMixin, ListView):
    model = GoalTemplate
    template_name = 'goals/template_list.html'
    context_object_name = 'templates'
    paginate_by = 20

class GoalTemplateCreateView(LoginRequiredMixin, CreateView):
    model = GoalTemplate
    template_name = 'goals/template_form.html'
    fields = ['name', 'description', 'template_type']
    success_url = reverse_lazy('goals:template_list')

class GoalTemplateDetailView(LoginRequiredMixin, DetailView):
    model = GoalTemplate
    template_name = 'goals/template_detail.html'
    context_object_name = 'template'

class GoalTemplateEditView(LoginRequiredMixin, UpdateView):
    model = GoalTemplate
    template_name = 'goals/template_form.html'
    fields = ['name', 'description', 'template_type']
    success_url = reverse_lazy('goals:template_list')

class GoalTemplateDeleteView(LoginRequiredMixin, DeleteView):
    model = GoalTemplate
    template_name = 'goals/template_confirm_delete.html'
    success_url = reverse_lazy('goals:template_list')
