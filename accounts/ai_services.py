"""
AI Services for Inspora platform.
Handles chat responses, smart suggestions, and workflow assistance.
"""
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from django.utils import timezone
from .models import AIChat, AIChatMessage, AISuggestion, AIKnowledgeBase


class AIChatService:
    """Service for handling AI chat conversations."""
    
    # Pre-defined responses for common questions
    COMMON_RESPONSES = {
        'how_to_create_project': {
            'response': "To create a project in Inspora:\n\n1. Click on 'Projects' in the navigation\n2. Click the 'Create Project' button\n3. Fill in the project details (name, description, team, etc.)\n4. Click 'Create Project'\n\nWould you like me to show you more details about any specific step?",
            'suggestions': ['Create your first project', 'Learn about project templates', 'Set up project sections']
        },
        'how_to_manage_tasks': {
            'response': "Task management in Inspora is straightforward:\n\n• Create tasks from the Tasks page or within projects\n• Assign tasks to team members\n• Set due dates and priorities\n• Track progress and status\n• Add comments and attachments\n\nWhat specific aspect of task management would you like to learn more about?",
            'suggestions': ['Create a new task', 'Learn about task dependencies', 'Set up task templates']
        },
        'how_to_use_teams': {
            'response': "Teams in Inspora help you organize work and collaborate:\n\n• Create teams to group related projects\n• Add team members with different roles\n• Manage permissions and access\n• Track team performance\n\nWould you like me to help you create a team or add members?",
            'suggestions': ['Create a new team', 'Add team members', 'Learn about team roles']
        },
        'general_help': {
            'response': "I'm here to help you with Inspora! I can assist with:\n\n• Project and task management\n• Team collaboration\n• Workflow optimization\n• Platform features and tips\n\nWhat would you like to know more about?",
            'suggestions': ['Get started guide', 'Feature overview', 'Best practices']
        }
    }
    
    @classmethod
    def get_response(cls, user_message: str, user, chat_session_id: str = None) -> Dict[str, Any]:
        """Generate AI response based on user message."""
        
        # Create or get existing chat session
        chat, created = AIChat.objects.get_or_create(
            user=user,
            session_id=chat_session_id or f"chat_{user.id}_{int(timezone.now().timestamp())}",
            defaults={'title': 'AI Assistant Chat'}
        )
        
        # Save user message
        user_msg = AIChatMessage.objects.create(
            chat=chat,
            message_type='user',
            content=user_message
        )
        
        # Generate AI response
        ai_response = cls._generate_response(user_message, user)
        
        # Save AI response
        ai_msg = AIChatMessage.objects.create(
            chat=chat,
            message_type='ai',
            content=ai_response['response'],
            metadata={'suggestions': ai_response.get('suggestions', [])}
        )
        
        # Update chat title if it's new
        if created and not chat.title:
            chat.title = user_message[:50] + '...' if len(user_message) > 50 else user_message
            chat.save()
        
        return {
            'response': ai_response['response'],
            'suggestions': ai_response.get('suggestions', []),
            'chat_id': chat.id,
            'session_id': chat.session_id
        }
    
    @classmethod
    def _generate_response(cls, message: str, user) -> Dict[str, Any]:
        """Generate contextual response based on message content."""
        message_lower = message.lower()
        
        # Check for common patterns
        if any(word in message_lower for word in ['project', 'create project', 'new project']):
            return cls.COMMON_RESPONSES['how_to_create_project']
        elif any(word in message_lower for word in ['task', 'manage task', 'create task']):
            return cls.COMMON_RESPONSES['how_to_manage_tasks']
        elif any(word in message_lower for word in ['team', 'create team', 'manage team']):
            return cls.COMMON_RESPONSES['how_to_use_teams']
        elif any(word in message_lower for word in ['help', 'support', 'how to', 'what is']):
            return cls.COMMON_RESPONSES['general_help']
        else:
            # Generate contextual response
            return cls._generate_contextual_response(message, user)
    
    @classmethod
    def _generate_contextual_response(cls, message: str, user) -> Dict[str, Any]:
        """Generate contextual response based on user's current state."""
        # Check user's recent activity and generate relevant suggestions
        recent_projects = user.owned_projects.all()[:3]
        recent_tasks = user.assigned_tasks.all()[:3]
        
        if recent_projects:
            project_names = [p.name for p in recent_projects]
            return {
                'response': f"I see you've been working on projects like {', '.join(project_names)}. How can I help you with these projects or something new?",
                'suggestions': ['View project details', 'Create new project', 'Manage project tasks']
            }
        elif recent_tasks:
            return {
                'response': "I notice you have some tasks assigned. Would you like help organizing them, setting priorities, or creating new ones?",
                'suggestions': ['View my tasks', 'Create new task', 'Organize task list']
            }
        else:
            return {
                'response': "Welcome to Inspora! I'm here to help you get started. What would you like to do first?",
                'suggestions': ['Create your first project', 'Set up a team', 'Learn the basics']
            }


class AISuggestionService:
    """Service for generating AI-powered suggestions."""
    
    @classmethod
    def generate_suggestions(cls, user) -> List[AISuggestion]:
        """Generate personalized suggestions for the user."""
        suggestions = []
        
        # Check for task optimization opportunities
        overdue_tasks = user.assigned_tasks.filter(
            due_date__lt=timezone.now().date(),
            status__in=['todo', 'in_progress']
        )
        
        if overdue_tasks.exists():
            suggestions.append(
                AISuggestion(
                    user=user,
                    suggestion_type='task_optimization',
                    title='Overdue Tasks Detected',
                    description=f'You have {overdue_tasks.count()} overdue tasks. Consider updating their status or extending deadlines.',
                    action_url='/tasks/overdue/',
                    action_text='View Overdue Tasks',
                    priority=4
                )
            )
        
        # Check for project management opportunities
        active_projects = user.owned_projects.filter(status='active')
        if active_projects.count() > 5:
            suggestions.append(
                AISuggestion(
                    user=user,
                    suggestion_type='project_management',
                    title='Multiple Active Projects',
                    description='You have many active projects. Consider reviewing and prioritizing them for better focus.',
                    action_url='/projects/',
                    action_text='Review Projects',
                    priority=3
                )
            )
        
        # Check for team collaboration opportunities
        if not user.team_memberships.exists():
            suggestions.append(
                AISuggestion(
                    user=user,
                    suggestion_type='team_collaboration',
                    title='Join or Create a Team',
                    description='Teams help organize work and improve collaboration. Consider joining an existing team or creating a new one.',
                    action_url='/teams/',
                    action_text='Explore Teams',
                    priority=2
                )
            )
        
        # Productivity tips
        if user.assigned_tasks.filter(status='todo').count() > 10:
            suggestions.append(
                AISuggestion(
                    user=user,
                    suggestion_type='productivity_tip',
                    title='Task Organization Tip',
                    description='You have many pending tasks. Try grouping them by priority or deadline to improve focus.',
                    action_url='/tasks/',
                    action_text='Organize Tasks',
                    priority=2
                )
            )
        
        return suggestions
    
    @classmethod
    def create_suggestion(cls, user, suggestion_type: str, title: str, description: str, 
                         action_url: str = '', action_text: str = '', priority: int = 1) -> AISuggestion:
        """Create a new AI suggestion."""
        return AISuggestion.objects.create(
            user=user,
            suggestion_type=suggestion_type,
            title=title,
            description=description,
            action_url=action_url,
            action_text=action_text,
            priority=priority
        )


class AIWorkflowService:
    """Service for AI-powered workflow assistance."""
    
    @classmethod
    def analyze_user_workflow(cls, user) -> Dict[str, Any]:
        """Analyze user's current workflow and provide insights."""
        analysis = {
            'total_projects': user.owned_projects.count(),
            'active_projects': user.owned_projects.filter(status='active').count(),
            'completed_projects': user.owned_projects.filter(status='completed').count(),
            'total_tasks': user.assigned_tasks.count(),
            'completed_tasks': user.assigned_tasks.filter(status='completed').count(),
            'overdue_tasks': user.assigned_tasks.filter(
                due_date__lt=timezone.now().date(),
                status__in=['todo', 'in_progress']
            ).count(),
            'team_memberships': user.team_memberships.count(),
            'productivity_score': 0
        }
        
        # Calculate productivity score
        if analysis['total_tasks'] > 0:
            completion_rate = analysis['completed_tasks'] / analysis['total_tasks']
            analysis['productivity_score'] = int(completion_rate * 100)
        
        return analysis
    
    @classmethod
    def suggest_workflow_improvements(cls, user) -> List[str]:
        """Suggest workflow improvements based on user analysis."""
        analysis = cls.analyze_user_workflow(user)
        suggestions = []
        
        if analysis['overdue_tasks'] > 0:
            suggestions.append("Consider implementing a daily task review to prevent overdue tasks.")
        
        if analysis['active_projects'] > 5:
            suggestions.append("Focus on fewer projects simultaneously to improve completion rates.")
        
        if analysis['productivity_score'] < 70:
            suggestions.append("Try breaking down larger tasks into smaller, manageable subtasks.")
        
        if analysis['team_memberships'] == 0:
            suggestions.append("Collaborate with team members to improve project outcomes.")
        
        return suggestions


class AIKnowledgeService:
    """Service for AI knowledge base management."""
    
    @classmethod
    def search_knowledge(cls, query: str, limit: int = 5) -> List[AIKnowledgeBase]:
        """Search knowledge base for relevant information."""
        # Simple keyword-based search (can be enhanced with vector search)
        keywords = query.lower().split()
        
        results = []
        for article in AIKnowledgeBase.objects.filter(is_active=True):
            score = 0
            title_lower = article.title.lower()
            content_lower = article.content.lower()
            
            for keyword in keywords:
                if keyword in title_lower:
                    score += 3  # Title matches are more important
                if keyword in content_lower:
                    score += 1
                if keyword in article.tags:
                    score += 2
            
            if score > 0:
                results.append((article, score))
        
        # Sort by score and return top results
        results.sort(key=lambda x: x[1], reverse=True)
        return [article for article, score in results[:limit]]
    
    @classmethod
    def get_contextual_help(cls, context: str, user) -> List[AIKnowledgeBase]:
        """Get contextual help based on user's current context."""
        # This can be enhanced to analyze user's current page/action
        if 'project' in context.lower():
            return AIKnowledgeBase.objects.filter(
                category='project_management',
                is_active=True
            )[:3]
        elif 'task' in context.lower():
            return AIKnowledgeBase.objects.filter(
                category='task_management',
                is_active=True
            )[:3]
        elif 'team' in context.lower():
            return AIKnowledgeBase.objects.filter(
                category='team_collaboration',
                is_active=True
            )[:3]
        else:
            return AIKnowledgeBase.objects.filter(is_active=True)[:3]
