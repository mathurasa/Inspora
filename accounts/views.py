"""
Views for accounts app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as AuthLoginView
from django.contrib.auth import logout
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views import View
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from PIL import Image
import io
import base64
import os
from .models import Team, TeamMembership, AIChat, AISuggestion, AIWorkflowAssistant, AIKnowledgeBase
from .ai_services import AIChatService, AISuggestionService, AIWorkflowService
from .forms import CustomUserCreationForm
from .google_auth import get_google_oauth2_url, exchange_code_for_token, get_user_info_from_token
import json
from django.core.exceptions import ValidationError
from django.conf import settings
from .forms import PricingRegistrationForm
from .services.google_drive import GoogleDriveService
from .services.github import GitHubService
from .models import Document, DocumentVersion, GoogleDriveIntegration, GitHubIntegration
from django.db import models
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
import time
from django.contrib import messages

User = get_user_model()





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
    fields = ['first_name', 'last_name', 'email', 'job_title', 'department', 'bio', 'avatar']
    
    def get_object(self, queryset=None):
        """Return the current user's profile."""
        return self.request.user
    
    def get_success_url(self):
        return reverse_lazy('accounts:profile')
    
    def form_valid(self, form):
        """Handle avatar upload and processing."""
        if 'avatar' in form.files:
            avatar_file = form.files['avatar']
            
            # Validate file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if avatar_file.content_type not in allowed_types:
                from django.contrib import messages
                messages.error(self.request, 'Invalid file type. Please use JPEG, PNG, GIF, or WebP.')
                return self.form_invalid(form)
            
            # Validate file size (5MB)
            if avatar_file.size > 5 * 1024 * 1024:
                from django.contrib import messages
                messages.error(self.request, 'File size too large. Maximum size is 5MB.')
                return self.form_invalid(form)
            
            # Process and save the image
            try:
                from PIL import Image
                import io
                
                # Open image with Pillow
                img = Image.open(avatar_file)
                
                # Convert to RGB if necessary (for PNG with transparency)
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if too large (max 800x800)
                max_size = (800, 800)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Save to BytesIO
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=85, optimize=True)
                output.seek(0)
                
                # Create a new file-like object
                from django.core.files.base import ContentFile
                processed_file = ContentFile(output.getvalue())
                
                # Delete old avatar if it exists
                if self.object.avatar:
                    old_avatar_path = self.object.avatar.path
                    if os.path.exists(old_avatar_path):
                        os.remove(old_avatar_path)
                
                # Save new avatar
                filename = f"avatar_{self.object.username}_{int(time.time())}.jpg"
                self.object.avatar.save(filename, processed_file, save=False)
                
            except Exception as e:
                from django.contrib import messages
                messages.error(self.request, f'Error processing image: {str(e)}')
                return self.form_invalid(form)
        
        return super().form_valid(form)








class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    template_name = 'accounts/team_form.html'
    fields = ['name', 'description', 'is_public', 'max_members']
    
    def form_valid(self, form):
        """Set the created_by field to the current user."""
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Create team membership for the creator as owner
        TeamMembership.objects.create(
            user=self.request.user,
            team=self.object,
            role='owner'
        )
        
        return response


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
    """Enhanced user registration view with better UX."""
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def get_context_data(self, **kwargs):
        """Add extra context for better UX."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Your Account'
        context['page_description'] = 'Join thousands of teams using Inspora to get more done'
        return context
    
    def form_valid(self, form):
        """Handle successful form submission with enhanced feedback."""
        try:
            # Save the user
            user = form.save()
            
            # Add success message
            from django.contrib import messages
            messages.success(
                self.request,
                f'🎉 Welcome to Inspora, {user.first_name}! Your account has been created successfully. '
                'Please check your email for a confirmation link and sign in below.'
            )
            
            # Log the registration for analytics
            print(f"New user registered: {user.username} ({user.email})")
            
            return super().form_valid(form)
            
        except Exception as e:
            # Handle any errors gracefully
            from django.contrib import messages
            messages.error(
                self.request,
                'There was an issue creating your account. Please try again or contact support.'
            )
            print(f"Registration error: {e}")
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors with better UX."""
        from django.contrib import messages
        
        # Show specific error messages
        if 'username' in form.errors:
            messages.error(self.request, 'Username is already taken. Please choose a different one.')
        elif 'email' in form.errors:
            messages.error(self.request, 'This email is already registered. Please use a different email or sign in.')
        elif 'password2' in form.errors:
            messages.error(self.request, 'Passwords do not match. Please try again.')
        else:
            messages.error(self.request, 'Please correct the errors below and try again.')
        
        return super().form_invalid(form)


class PricingRegistrationView(CreateView):
    """
    Enhanced registration view with pricing plan selection and payment processing.
    """
    form_class = PricingRegistrationForm
    template_name = 'accounts/pricing_register.html'
    success_url = reverse_lazy('accounts:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Set default values for plans
        context['selected_plan'] = self.request.GET.get('plan', 'free')
        context['billing_cycle'] = self.request.GET.get('billing', 'monthly')
        
        return context
    
    def form_valid(self, form):
        """Handle successful form submission."""
        response = super().form_valid(form)
        
        # Add success message
        from django.contrib import messages
        messages.success(
            self.request,
            'Account created successfully! Please sign in with your new credentials.'
        )
        
        return response


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
def ai_assistant_dashboard(request):
    """Comprehensive AI assistant dashboard view."""
    from .ai_services import AIChatService, AISuggestionService, AIWorkflowService, AIKnowledgeService
    
    # Get user context and AI insights
    user_context = AIChatService._get_user_context(request.user)
    
    # Get recent AI suggestions
    recent_suggestions = AISuggestion.objects.filter(
        user=request.user, 
        is_active=True
    ).order_by('-priority', '-created_at')[:5]
    
    # Get workflow analysis
    workflow_analysis = AIWorkflowService.analyze_user_workflow(request.user)
    workflow_suggestions = AIWorkflowService.suggest_workflow_improvements(request.user)
    
    # Get recent AI chats
    recent_chats = AIChat.objects.filter(
        user=request.user, 
        is_active=True
    ).order_by('-updated_at')[:3]
    
    # Get knowledge base recommendations
    knowledge_recommendations = AIKnowledgeService.get_contextual_help('general', request.user)
    
    # Get AI usage statistics
    ai_usage_stats = {
        'total_chats': AIChat.objects.filter(user=request.user).count(),
        'total_suggestions': AISuggestion.objects.filter(user=request.user).count(),
        'applied_suggestions': AISuggestion.objects.filter(user=request.user, is_applied=True).count(),
        'knowledge_articles': AIKnowledgeBase.objects.filter(is_active=True).count()
    }
    
    context = {
        'user_context': user_context,
        'recent_suggestions': recent_suggestions,
        'workflow_analysis': workflow_analysis,
        'workflow_suggestions': workflow_suggestions,
        'recent_chats': recent_chats,
        'knowledge_recommendations': knowledge_recommendations,
        'ai_usage_stats': ai_usage_stats,
        'page_title': 'AI Assistant Dashboard'
    }
    
    return render(request, 'accounts/ai_assistant_dashboard.html', context)


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


# Lightweight meeting/calendar helpers
def meet_now(request):
    """Redirect to Google Meet new meeting link."""
    return redirect('https://meet.google.com/new')


def calendar_quick_add(request):
    """Redirect to Google Calendar event creation with prefilled fields.

    Query params (all optional):
    - title: event title (default: Inspora Meeting)
    - start: ISO datetime string (e.g., 2025-08-15T10:00) in local time
    - duration: minutes (default: 30)
    - details: event description
    - add: comma-separated emails to add as guests
    """
    from urllib.parse import urlencode
    from django.utils.dateparse import parse_datetime
    from django.utils import timezone as dj_timezone

    title = (request.GET.get('title') or 'Inspora Meeting').strip()
    details = (request.GET.get('details') or '').strip()
    duration_minutes_raw = request.GET.get('duration') or '30'
    guest_emails = (request.GET.get('add') or '').strip()

    # Parse start time; default to now + 5 minutes
    start_param = request.GET.get('start')
    start_dt = parse_datetime(start_param) if start_param else None
    if start_dt is None:
        start_dt = dj_timezone.now() + timedelta(minutes=5)
    if dj_timezone.is_naive(start_dt):
        start_dt = dj_timezone.make_aware(start_dt, dj_timezone.get_current_timezone())

    # Duration
    try:
        duration_minutes = max(5, min(720, int(duration_minutes_raw)))
    except (TypeError, ValueError):
        duration_minutes = 30

    end_dt = start_dt + timedelta(minutes=duration_minutes)

    # Format datetimes for Google Calendar URL (UTC, basic format)
    start_utc = start_dt.astimezone(dj_timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    end_utc = end_dt.astimezone(dj_timezone.utc).strftime('%Y%m%dT%H%M%SZ')

    query = {
        'text': title,
        'dates': f'{start_utc}/{end_utc}',
    }
    if details:
        query['details'] = details
    # Prefill details with hint to add Meet link if desired
    if 'details' not in query or not query['details']:
        query['details'] = 'Add Google Meet: (Click "Add video conferencing" in Calendar)'
    if guest_emails:
        query['add'] = guest_emails

    url = 'https://calendar.google.com/calendar/u/0/r/eventedit?' + urlencode(query)
    return redirect(url)


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
    try:
        auth_url = get_google_oauth2_url()
        return redirect(auth_url)
    except ValidationError as e:
        messages.error(request, f'Google OAuth2 not configured: {str(e)}')
        return redirect('accounts:login')
    except Exception as e:
        messages.error(request, f'Google OAuth2 error: {str(e)}')
        return redirect('accounts:login')


def google_callback(request):
    """Handle Google OAuth2 callback."""
    try:
        # Check if Google OAuth2 is properly configured
        if not settings.GOOGLE_OAUTH2_CLIENT_ID or not settings.GOOGLE_OAUTH2_CLIENT_SECRET:
            messages.error(request, 'Google OAuth2 not configured. Please contact administrator.')
            return redirect('accounts:login')
        
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
            return redirect('public_landing')
        else:
            messages.error(request, 'Failed to authenticate with Google.')
            return redirect('accounts:login')
            
    except ValidationError as e:
        messages.error(request, f'Google OAuth2 configuration error: {str(e)}')
        return redirect('accounts:login')
    except Exception as e:
        messages.error(request, f'Google authentication error: {str(e)}')
        return redirect('accounts:login')


class DocumentListView(LoginRequiredMixin, ListView):
    """
    View for listing user documents from all sources.
    """
    model = Document
    template_name = 'accounts/document_list.html'
    context_object_name = 'documents'
    paginate_by = 20
    
    def get_queryset(self):
        """Get documents accessible to the user."""
        return Document.objects.filter(
            models.Q(user=self.request.user) |
            models.Q(shared_with=self.request.user) |
            models.Q(is_public=True)
        ).filter(is_active=True, is_deleted=False).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get integration status
        try:
            context['google_drive_status'] = GoogleDriveIntegration.objects.get(
                user=self.request.user, is_active=True
            )
        except GoogleDriveIntegration.DoesNotExist:
            context['google_drive_status'] = None
        
        try:
            context['github_status'] = GitHubIntegration.objects.get(
                user=self.request.user, is_active=True
            )
        except GitHubIntegration.DoesNotExist:
            context['github_status'] = None
        
        # Get filter parameters
        context['source_filter'] = self.request.GET.get('source', '')
        context['file_type_filter'] = self.request.GET.get('file_type', '')
        context['search_query'] = self.request.GET.get('q', '')
        
        return context


class DocumentDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying document details.
    """
    model = Document
    template_name = 'accounts/document_detail.html'
    context_object_name = 'document'
    
    def get_queryset(self):
        """Get documents accessible to the user."""
        return Document.objects.filter(
            models.Q(user=self.request.user) |
            models.Q(shared_with=self.request.user) |
            models.Q(is_public=True)
        ).filter(is_active=True, is_deleted=False)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get document versions
        context['versions'] = self.object.versions.all()[:10]
        
        # Get related documents
        context['related_documents'] = Document.objects.filter(
            user=self.object.user,
            tags__overlap=self.object.tags,
            is_active=True,
            is_deleted=False
        ).exclude(id=self.object.id)[:5]
        
        return context


class GoogleDriveConnectView(LoginRequiredMixin, View):
    """
    View for connecting Google Drive account.
    """
    def get(self, request):
        """Show Google Drive connection page."""
        try:
            integration = GoogleDriveIntegration.objects.get(user=request.user, is_active=True)
            return redirect('accounts:google_drive_files')
        except GoogleDriveIntegration.DoesNotExist:
            pass
        
        return render(request, 'accounts/google_drive_connect.html')
    
    def post(self, request):
        """Handle Google Drive OAuth2 callback."""
        # This would typically handle the OAuth2 callback
        # For now, we'll create a mock integration
        try:
            integration = GoogleDriveIntegration.objects.create(
                user=request.user,
                access_token="mock_token",
                refresh_token="mock_refresh",
                token_expiry=timezone.now() + timedelta(hours=1),
                drive_name="My Google Drive"
            )
            
            messages.success(request, 'Google Drive connected successfully!')
            return redirect('accounts:google_drive_files')
            
        except Exception as e:
            messages.error(request, f'Error connecting Google Drive: {e}')
            return redirect('accounts:google_drive_connect')


class GoogleDriveFilesView(LoginRequiredMixin, View):
    """
    View for displaying Google Drive files.
    """
    def get(self, request):
        """Show Google Drive files."""
        try:
            integration = GoogleDriveIntegration.objects.get(user=request.user, is_active=True)
            
            # Get files from Google Drive
            try:
                drive_service = GoogleDriveService(request.user)
                files = drive_service.list_files()
            except Exception as e:
                files = []
                messages.warning(request, f'Error fetching Google Drive files: {e}')
            
            return render(request, 'accounts/google_drive_files.html', {
                'files': files,
                'integration': integration
            })
            
        except GoogleDriveIntegration.DoesNotExist:
            messages.error(request, 'Google Drive not connected. Please connect first.')
            return redirect('accounts:google_drive_connect')


class GitHubConnectView(LoginRequiredMixin, View):
    """
    View for connecting GitHub account.
    """
    def get(self, request):
        """Show GitHub connection page."""
        try:
            integration = GitHubIntegration.objects.get(user=request.user, is_active=True)
            return redirect('accounts:github_repos')
        except GitHubIntegration.DoesNotExist:
            pass
        
        return render(request, 'accounts/github_connect.html')
    
    def post(self, request):
        """Handle GitHub OAuth2 callback."""
        # This would typically handle the OAuth2 callback
        # For now, we'll create a mock integration
        try:
            integration = GitHubIntegration.objects.create(
                user=request.user,
                access_token="mock_token",
                github_username="mock_user",
                github_email="mock@example.com"
            )
            
            messages.success(request, 'GitHub connected successfully!')
            return redirect('accounts:github_repos')
            
        except Exception as e:
            messages.error(request, f'Error connecting GitHub: {e}')
            return redirect('accounts:github_connect')


class GitHubReposView(LoginRequiredMixin, View):
    """
    View for displaying GitHub repositories.
    """
    def get(self, request):
        """Show GitHub repositories."""
        try:
            integration = GitHubIntegration.objects.get(user=request.user, is_active=True)
            
            # Get repositories from GitHub
            try:
                github_service = GitHubService(request.user)
                repos = github_service.list_repositories()
            except Exception as e:
                repos = []
                messages.warning(request, f'Error fetching GitHub repositories: {e}')
            
            return render(request, 'accounts/github_repos.html', {
                'repos': repos,
                'integration': integration
            })
            
        except GitHubIntegration.DoesNotExist:
            messages.error(request, 'GitHub not connected. Please connect first.')
            return redirect('accounts:github_connect')


class DocumentDownloadView(LoginRequiredMixin, View):
    """
    View for downloading documents.
    """
    def get(self, request, pk):
        """Download a document."""
        try:
            document = Document.objects.filter(
                pk=pk,
                is_active=True,
                is_deleted=False
            ).filter(
                models.Q(user=request.user) |
                models.Q(shared_with=request.user) |
                models.Q(is_public=True)
            ).first()
            
            if not document:
                raise Document.DoesNotExist
            
            # Handle different source types
            if document.source == 'google_drive':
                return self._download_from_google_drive(request, document)
            elif document.source == 'github':
                return self._download_from_github(request, document)
            elif document.source == 'local' and document.local_file:
                return self._download_local_file(request, document)
            else:
                # Redirect to source URL
                return redirect(document.source_url)
                
        except Document.DoesNotExist:
            messages.error(request, 'Document not found.')
            return redirect('accounts:document_list')
    
    def _download_from_google_drive(self, request, document):
        """Download from Google Drive."""
        try:
            drive_service = GoogleDriveService(request.user)
            file_content = drive_service.download_file(document.source_id)
            
            if file_content:
                response = HttpResponse(file_content.read(), content_type=document.mime_type)
                response['Content-Disposition'] = f'attachment; filename="{document.file_name}"'
                return response
            else:
                messages.error(request, 'Error downloading from Google Drive.')
                return redirect('accounts:document_detail', pk=document.pk)
                
        except Exception as e:
            messages.error(request, f'Error downloading from Google Drive: {e}')
            return redirect('accounts:document_detail', pk=document.pk)
    
    def _download_from_github(self, request, document):
        """Download from GitHub."""
        try:
            # Extract repo and file path from folder
            folder_parts = document.folder.split('/')
            if len(folder_parts) >= 2:
                repo_name = folder_parts[0]
                file_path = '/'.join(folder_parts[1:]) + '/' + document.file_name
                
                github_service = GitHubService(request.user)
                file_content = github_service.download_file(repo_name, file_path)
                
                if file_content:
                    response = HttpResponse(file_content, content_type=document.mime_type)
                    response['Content-Disposition'] = f'attachment; filename="{document.file_name}"'
                    return response
                else:
                    messages.error(request, 'Error downloading from GitHub.')
                    return redirect('accounts:document_detail', pk=document.pk)
            else:
                messages.error(request, 'Invalid GitHub file path.')
                return redirect('accounts:document_detail', pk=document.pk)
                
        except Exception as e:
            messages.error(request, f'Error downloading from GitHub: {e}')
            return redirect('accounts:document_detail', pk=document.pk)
    
    def _download_local_file(self, request, document):
        """Download local file."""
        try:
            response = HttpResponse(document.local_file.read(), content_type=document.mime_type)
            response['Content-Disposition'] = f'attachment; filename="{document.file_name}"'
            return response
        except Exception as e:
            messages.error(request, f'Error downloading local file: {e}')
            return redirect('accounts:document_detail', pk=document.pk)


class DocumentSyncView(LoginRequiredMixin, View):
    """
    View for syncing documents from external sources.
    """
    def post(self, request):
        """Sync documents from connected services."""
        source = request.POST.get('source')
        
        if source == 'google_drive':
            return self._sync_google_drive(request)
        elif source == 'github':
            return self._sync_github(request)
        else:
            messages.error(request, 'Invalid source specified.')
            return redirect('accounts:document_list')
    
    def _sync_google_drive(self, request):
        """Sync documents from Google Drive."""
        try:
            drive_service = GoogleDriveService(request.user)
            success = drive_service.sync_documents()
            
            if success:
                messages.success(request, 'Google Drive documents synced successfully!')
            else:
                messages.warning(request, 'Some documents failed to sync from Google Drive.')
                
        except Exception as e:
            messages.error(request, f'Error syncing Google Drive: {e}')
        
        return redirect('accounts:document_list')
    
    def _sync_github(self, request):
        """Sync documents from GitHub."""
        try:
            github_service = GitHubService(request.user)
            success = github_service.sync_documents()
            
            if success:
                messages.success(request, 'GitHub documents synced successfully!')
            else:
                messages.warning(request, 'Some documents failed to sync from GitHub.')
                
        except Exception as e:
            messages.error(request, f'Error syncing GitHub: {e}')
        
        return redirect('accounts:document_list')


@login_required
def user_settings_view(request):
    """User settings view."""
    context = {
        'page_title': 'User Settings',
        'page_description': 'Manage your account settings and preferences',
        'user': request.user,
    }
    return render(request, 'accounts/user_settings.html', context)


@login_required
def admin_dashboard(request):
    """Admin dashboard view for system overview and administration."""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('public_landing')
    
    # Get system statistics
    context = {
        'total_users': User.objects.count(),
        'total_projects': 0,  # Will be updated when projects app is properly integrated
        'total_tasks': 0,     # Will be updated when tasks app is properly integrated
        'total_teams': Team.objects.count(),
        'recent_users': User.objects.order_by('-date_joined')[:5],
        'recent_activity': [],  # Can be enhanced with activity logging
        'system_status': {
            'database': 'Online',
            'cache': 'Online',
            'storage': 'Online',
            'api': 'Online'
        }
    }
    
    return render(request, 'admin/dashboard.html', context)
