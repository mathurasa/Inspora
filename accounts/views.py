"""
Views for accounts app.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as AuthLoginView
from django.contrib.auth import logout
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from .models import Team, TeamMembership, AIChat, AISuggestion, AIWorkflowAssistant
from .ai_services import AIChatService, AISuggestionService, AIWorkflowService
from .forms import CustomUserCreationForm
from .google_auth import get_google_oauth2_url, exchange_code_for_token, get_user_info_from_token
import json

User = get_user_model()


@login_required
def user_dashboard(request):
    """User dashboard view."""
    return render(request, 'dashboard.html')


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 20


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/user_detail.html'
    context_object_name = 'user'


class TeamListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = 'accounts/team_list.html'
    context_object_name = 'teams'
    paginate_by = 20


class TeamDetailView(LoginRequiredMixin, DetailView):
    model = Team
    template_name = 'accounts/team_detail.html'
    context_object_name = 'team'


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/user_profile.html'
    context_object_name = 'user'
    
    def get_object(self, queryset=None):
        """Return the current user's profile."""
        return self.request.user


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'accounts/user_profile_edit.html'
    fields = ['first_name', 'last_name', 'email', 'job_title', 'department', 'bio']
    
    def get_object(self, queryset=None):
        """Return the current user's profile."""
        return self.request.user
    
    def get_success_url(self):
        return reverse_lazy('accounts:profile')


class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    template_name = 'accounts/team_form.html'
    fields = ['name', 'description', 'is_public', 'max_members']


class TeamEditView(LoginRequiredMixin, UpdateView):
    model = Team
    template_name = 'accounts/team_form.html'
    fields = ['name', 'description', 'is_public', 'max_members']


class TeamMembersView(LoginRequiredMixin, ListView):
    model = TeamMembership
    template_name = 'accounts/team_members.html'
    context_object_name = 'memberships'
    
    def get_queryset(self):
        return TeamMembership.objects.filter(team_id=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team'] = Team.objects.get(pk=self.kwargs['pk'])
        return context


class LoginView(AuthLoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


from django.contrib import messages

def logout_confirm(request):
    """Show logout confirmation page."""
    if not request.user.is_authenticated:
        messages.warning(request, 'You are not logged in.')
        return redirect('accounts:login')
    
    return render(request, 'accounts/logout_confirm.html')


def logout_view(request):
    """Handle user logout."""
    if request.user.is_authenticated:
        # Log the logout action
        username = request.user.username
        logout(request)
        messages.success(request, f'You have been successfully logged out, {username}.')
    else:
        messages.info(request, 'You were not logged in.')
    
    return redirect('accounts:login')


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')


# Static page views
def pricing_view(request):
    """Pricing page view."""
    return render(request, 'accounts/pricing.html')


def resources_view(request):
    """Resources main page view."""
    return render(request, 'accounts/resources.html')


def help_center_view(request):
    """Help center page view."""
    return render(request, 'accounts/help_center.html')


def academy_view(request):
    """Inspora Academy page view."""
    return render(request, 'accounts/academy.html')


def certifications_view(request):
    """Certifications page view."""
    return render(request, 'accounts/certifications.html')


def forums_view(request):
    """Community forums page view."""
    return render(request, 'accounts/forums.html')


def work_management_view(request):
    """Work management hub page view."""
    return render(request, 'accounts/work_management.html')


def customer_stories_view(request):
    """Customer stories page view."""
    return render(request, 'accounts/customer_stories.html')


def events_view(request):
    """Events and webinars page view."""
    return render(request, 'accounts/events.html')


def support_view(request):
    """Support page view."""
    return render(request, 'accounts/support.html')


def developer_view(request):
    """Developer support page view."""
    return render(request, 'accounts/developer.html')


def partners_view(request):
    """Partners page view."""
    return render(request, 'accounts/partners.html')


def contact_view(request):
    """Contact page view."""
    return render(request, 'accounts/contact.html', {
        'title': 'Contact Us - Inspora'
    })


def templates_view(request):
    """Templates main page view."""
    return render(request, 'accounts/templates.html')


def project_templates_view(request):
    """Project templates page view."""
    return render(request, 'accounts/project_templates.html')


def goal_templates_view(request):
    """Goal templates page view."""
    return render(request, 'accounts/goal_templates.html')


def meeting_templates_view(request):
    """Meeting templates page view."""
    return render(request, 'accounts/meeting_templates.html')

# AI-related views
@login_required
def ai_chat_view(request):
    """AI chat interface view."""
    user_chats = AIChat.objects.filter(user=request.user, is_active=True).order_by('-updated_at')
    return render(request, 'accounts/ai_chat.html', {
        'chats': user_chats
    })


@login_required
def ai_suggestions_view(request):
    """AI suggestions view."""
    suggestions = AISuggestion.objects.filter(user=request.user, is_active=True).order_by('-priority', '-created_at')
    return render(request, 'accounts/ai_suggestions.html', {
        'suggestions': suggestions
    })


@login_required
def ai_workflow_view(request):
    """AI workflow assistance view."""
    workflow_analysis = AIWorkflowService.analyze_user_workflow(request.user)
    workflow_suggestions = AIWorkflowService.suggest_workflow_improvements(request.user)
    
    return render(request, 'accounts/ai_workflow.html', {
        'analysis': workflow_analysis,
        'suggestions': workflow_suggestions
    })


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def ai_chat_api(request):
    """API endpoint for AI chat."""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        chat_session_id = data.get('session_id')
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Get AI response
        response = AIChatService.get_response(user_message, request.user, chat_session_id)
        
        return JsonResponse({
            'success': True,
            'response': response['response'],
            'suggestions': response['suggestions'],
            'chat_id': response['chat_id'],
            'session_id': response['session_id']
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def ai_generate_suggestions(request):
    """API endpoint to generate AI suggestions."""
    try:
        # Generate new suggestions
        suggestions = AISuggestionService.generate_suggestions(request.user)
        
        # Save suggestions to database
        saved_suggestions = []
        for suggestion in suggestions:
            suggestion.save()
            saved_suggestions.append({
                'id': suggestion.id,
                'title': suggestion.title,
                'description': suggestion.description,
                'type': suggestion.get_suggestion_type_display(),
                'priority': suggestion.priority,
                'action_url': suggestion.action_url,
                'action_text': suggestion.action_text
            })
        
        return JsonResponse({
            'success': True,
            'suggestions': saved_suggestions,
            'count': len(saved_suggestions)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def ai_mark_suggestion_read(request, suggestion_id):
    """Mark a suggestion as read."""
    try:
        suggestion = AISuggestion.objects.get(id=suggestion_id, user=request.user)
        suggestion.is_read = True
        suggestion.save()
        
        return JsonResponse({'success': True})
        
    except AISuggestion.DoesNotExist:
        return JsonResponse({'error': 'Suggestion not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def ai_mark_suggestion_applied(request, suggestion_id):
    """Mark a suggestion as applied."""
    try:
        suggestion = AISuggestion.objects.get(id=suggestion_id, user=request.user)
        suggestion.is_applied = True
        suggestion.save()
        
        return JsonResponse({'success': True})
        
    except AISuggestion.DoesNotExist:
        return JsonResponse({'error': 'Suggestion not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def ai_knowledge_search(request):
    """AI knowledge base search view."""
    query = request.GET.get('q', '')
    results = []
    
    if query:
        from .ai_services import AIKnowledgeService
        results = AIKnowledgeService.search_knowledge(query)
    
    return render(request, 'accounts/ai_knowledge.html', {
        'query': query,
        'results': results
    })


def google_login(request):
    """Redirect user to Google OAuth2 authorization."""
    auth_url = get_google_oauth2_url()
    return redirect(auth_url)


def google_callback(request):
    """Handle Google OAuth2 callback."""
    try:
        # Get authorization code from callback
        code = request.GET.get('code')
        if not code:
            messages.error(request, 'Authorization code not received from Google.')
            return redirect('accounts:login')
        
        # Exchange code for access token
        token_data = exchange_code_for_token(code)
        access_token = token_data.get('access_token')
        
        if not access_token:
            messages.error(request, 'Failed to get access token from Google.')
            return redirect('accounts:login')
        
        # Get user information from Google
        user_info = get_user_info_from_token(access_token)
        
        # Authenticate or create user
        from django.contrib.auth import authenticate, login
        user = authenticate(request, google_id_token=user_info.get('id'))
        
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Failed to authenticate with Google.')
            return redirect('accounts:login')
            
    except Exception as e:
        messages.error(request, f'Google authentication error: {str(e)}')
        return redirect('accounts:login')
