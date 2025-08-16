"""
AI Services for Inspora platform.
Handles chat responses, smart suggestions, and workflow assistance.
"""
import json
import random
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
from django.utils import timezone
from django.db.models import Q, Count
from .models import AIChat, AIChatMessage, AISuggestion, AIKnowledgeBase, User


class AIChatService:
    """Enhanced service for handling AI chat conversations with context awareness."""
    
    # Enhanced pre-defined responses with more context
    COMMON_RESPONSES = {
        'how_to_create_project': {
            'response': "To create a project in Inspora:\n\n1. Click on 'Projects' in the navigation\n2. Click the 'Create Project' button\n3. Fill in the project details (name, description, team, etc.)\n4. Click 'Create Project'\n\nWould you like me to show you more details about any specific step?",
            'suggestions': ['Create your first project', 'Learn about project templates', 'Set up project sections'],
            'context': 'project_creation'
        },
        'how_to_manage_tasks': {
            'response': "Task management in Inspora is straightforward:\n\n• Create tasks from the Tasks page or within projects\n• Assign tasks to team members\n• Set due dates and priorities\n• Track progress and status\n• Add comments and attachments\n\nWhat specific aspect of task management would you like to learn more about?",
            'suggestions': ['Create a new task', 'Learn about task dependencies', 'Set up task templates'],
            'context': 'task_management'
        },
        'how_to_use_teams': {
            'response': "Teams in Inspora help you organize work and collaborate:\n\n• Create teams to group related projects\n• Add team members with different roles\n• Manage permissions and access\n• Track team performance\n\nWould you like me to help you create a team or add members?",
            'suggestions': ['Create a new team', 'Add team members', 'Learn about team roles'],
            'context': 'team_management'
        },
        'general_help': {
            'response': "I'm here to help you with Inspora! I can assist with:\n\n• Project and task management\n• Team collaboration\n• Workflow optimization\n• Platform features and tips\n\nWhat would you like to know more about?",
            'suggestions': ['Get started guide', 'Feature overview', 'Best practices'],
            'context': 'general'
        }
    }
    
    # Intent patterns for better understanding
    INTENT_PATTERNS = {
        'project_creation': [
            r'\b(create|start|begin|new)\s+(project|proj)',
            r'\bhow\s+to\s+(create|start|begin)\s+(a\s+)?project',
            r'\bproject\s+(creation|setup|start)'
        ],
        'task_management': [
            r'\b(task|todo|action)\s+(create|manage|organize)',
            r'\bhow\s+to\s+(create|manage|organize)\s+(tasks|todos)',
            r'\btask\s+(management|organization|planning)'
        ],
        'team_collaboration': [
            r'\b(team|collaborate|work\s+together)',
            r'\bhow\s+to\s+(create|manage|join)\s+(a\s+)?team',
            r'\bteam\s+(creation|management|collaboration)'
        ],
        'workflow_optimization': [
            r'\b(workflow|process|efficiency|optimize)',
            r'\bhow\s+to\s+(improve|optimize|streamline)',
            r'\bworkflow\s+(improvement|optimization|automation)'
        ],
        'reporting_analytics': [
            r'\b(report|analytics|metrics|dashboard)',
            r'\bhow\s+to\s+(view|generate|create)\s+(reports|analytics)',
            r'\breporting\s+(tools|features|capabilities)'
        ]
    }
    
    @classmethod
    def get_response(cls, user_message: str, user, chat_session_id: str = None) -> Dict[str, Any]:
        """Generate enhanced AI response based on user message and context."""
        
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
        
        # Generate enhanced AI response
        ai_response = cls._generate_enhanced_response(user_message, user, chat)
        
        # Save AI response
        ai_msg = AIChatMessage.objects.create(
            chat=chat,
            message_type='ai',
            content=ai_response['response'],
            metadata={
                'suggestions': ai_response.get('suggestions', []),
                'context': ai_response.get('context', ''),
                'intent': ai_response.get('intent', ''),
                'confidence': ai_response.get('confidence', 0.8)
            }
        )
        
        # Update chat title if it's new
        if created and not chat.title:
            chat.title = user_message[:50] + '...' if len(user_message) > 50 else user_message
            chat.save()
        
        return {
            'response': ai_response['response'],
            'suggestions': ai_response.get('suggestions', []),
            'chat_id': chat.id,
            'session_id': chat.session_id,
            'context': ai_response.get('context', ''),
            'intent': ai_response.get('intent', '')
        }
    
    @classmethod
    def _generate_enhanced_response(cls, message: str, user, chat=None) -> Dict[str, Any]:
        """Generate contextual response with intent recognition and personalization."""
        message_lower = message.lower()
        
        # Detect intent
        detected_intent = cls._detect_intent(message_lower)
        
        # Get user context
        user_context = cls._get_user_context(user)
        
        # Check for common patterns first
        if any(word in message_lower for word in ['project', 'create project', 'new project']):
            return cls._enhance_response_with_context(
                cls.COMMON_RESPONSES['how_to_create_project'],
                user_context,
                'project_creation'
            )
        elif any(word in message_lower for word in ['task', 'manage task', 'create task']):
            return cls._enhance_response_with_context(
                cls.COMMON_RESPONSES['how_to_manage_tasks'],
                user_context,
                'task_management'
            )
        elif any(word in message_lower for word in ['team', 'create team', 'manage team']):
            return cls._enhance_response_with_context(
                cls.COMMON_RESPONSES['how_to_use_teams'],
                user_context,
                'team_management'
            )
        elif any(word in message_lower for word in ['help', 'support', 'how to', 'what is']):
            return cls._enhance_response_with_context(
                cls.COMMON_RESPONSES['general_help'],
                user_context,
                'general'
            )
        else:
            # Generate contextual response based on intent and user context
            return cls._generate_intelligent_response(message, user, detected_intent, user_context, chat)
    
    @classmethod
    def _detect_intent(cls, message: str) -> str:
        """Detect user intent using pattern matching."""
        for intent, patterns in cls.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    return intent
        return 'general'
    
    @classmethod
    def _get_user_context(cls, user) -> Dict[str, Any]:
        """Get comprehensive user context for personalized responses."""
        try:
            return {
                'recent_projects': list(user.owned_projects.all()[:5].values('id', 'name', 'status')),
                'recent_tasks': list(user.assigned_tasks.all()[:5].values('id', 'title', 'status', 'due_date')),
                'team_memberships': list(user.team_memberships.all()[:3].values('team__name', 'role')),
                'overdue_tasks_count': user.assigned_tasks.filter(
                    due_date__lt=timezone.now().date(),
                    status__in=['todo', 'in_progress']
                ).count(),
                'active_projects_count': user.owned_projects.filter(status='active').count(),
                'last_login': user.last_login,
                'date_joined': user.date_joined
            }
        except Exception:
            return {}
    
    @classmethod
    def _enhance_response_with_context(cls, base_response: Dict, user_context: Dict, context_type: str) -> Dict:
        """Enhance base response with user-specific context."""
        enhanced_response = base_response.copy()
        
        if context_type == 'project_creation' and user_context.get('active_projects_count', 0) > 0:
            enhanced_response['response'] += f"\n\nI notice you already have {user_context['active_projects_count']} active projects. Would you like me to help you organize them or create a new one?"
        
        elif context_type == 'task_management' and user_context.get('overdue_tasks_count', 0) > 0:
            enhanced_response['response'] += f"\n\nI see you have {user_context['overdue_tasks_count']} overdue tasks. Would you like help prioritizing or rescheduling them?"
        
        elif context_type == 'team_management' and not user_context.get('team_memberships'):
            enhanced_response['response'] += "\n\nI notice you're not part of any teams yet. Teams can greatly improve collaboration and project success!"
        
        return enhanced_response
    
    @classmethod
    def _generate_intelligent_response(cls, message: str, user, intent: str, user_context: Dict, chat=None) -> Dict[str, Any]:
        """Generate intelligent response based on intent and context."""
        
        # Get chat history for context
        chat_context = cls._get_chat_context(chat) if chat else []
        
        if intent == 'workflow_optimization':
            return cls._generate_workflow_response(user, user_context, chat_context)
        elif intent == 'reporting_analytics':
            return cls._generate_reporting_response(user, user_context)
        elif intent == 'project_management':
            return cls._generate_project_management_response(user, user_context)
        else:
            return cls._generate_contextual_response(message, user, user_context, chat_context)
    
    @classmethod
    def _get_chat_context(cls, chat) -> List[str]:
        """Get recent chat context for better conversation flow."""
        if not chat:
            return []
        
        recent_messages = chat.messages.filter(
            message_type__in=['user', 'ai']
        ).order_by('-created_at')[:5]
        
        return [msg.content for msg in recent_messages]
    
    @classmethod
    def _generate_workflow_response(cls, user, user_context: Dict, chat_context: List[str]) -> Dict[str, Any]:
        """Generate workflow optimization response."""
        overdue_count = user_context.get('overdue_tasks_count', 0)
        active_projects = user_context.get('active_projects_count', 0)
        
        if overdue_count > 0:
            return {
                'response': f"I notice you have {overdue_count} overdue tasks. Here are some workflow improvements:\n\n• Implement daily task reviews\n• Set realistic deadlines with buffer time\n• Use task dependencies to prevent bottlenecks\n• Consider task batching for similar activities",
                'suggestions': ['View overdue tasks', 'Create task templates', 'Set up daily reminders'],
                'context': 'workflow_optimization',
                'intent': 'workflow_optimization'
            }
        elif active_projects > 5:
            return {
                'response': f"You have {active_projects} active projects. For better workflow management:\n\n• Focus on 2-3 high-priority projects at a time\n• Use project templates for consistency\n• Implement regular project reviews\n• Delegate tasks to team members",
                'suggestions': ['Review project priorities', 'Create project templates', 'Delegate tasks'],
                'context': 'workflow_optimization',
                'intent': 'workflow_optimization'
            }
        else:
            return {
                'response': "Your workflow looks well-balanced! Here are some optimization tips:\n\n• Use time blocking for focused work\n• Implement the Pomodoro technique\n• Regular breaks improve productivity\n• Review and adjust your workflow monthly",
                'suggestions': ['Set up time blocking', 'Learn productivity techniques', 'Schedule workflow review'],
                'context': 'workflow_optimization',
                'intent': 'workflow_optimization'
            }
    
    @classmethod
    def _generate_reporting_response(cls, user, user_context: Dict) -> Dict[str, Any]:
        """Generate reporting and analytics response."""
        return {
            'response': "Inspora provides comprehensive reporting and analytics:\n\n• Project progress dashboards\n• Team performance metrics\n• Task completion analytics\n• Time tracking reports\n• Custom report builder\n\nWhat type of reports would you like to explore?",
            'suggestions': ['View project dashboard', 'Check team metrics', 'Generate custom reports'],
            'context': 'reporting_analytics',
            'intent': 'reporting_analytics'
        }
    
    @classmethod
    def _generate_project_management_response(cls, user, user_context: Dict) -> Dict[str, Any]:
        """Generate project management response."""
        active_projects = user_context.get('active_projects_count', 0)
        
        if active_projects > 0:
            return {
                'response': f"You have {active_projects} active projects. Here are some project management tips:\n\n• Use project templates for consistency\n• Set clear milestones and deadlines\n• Regular team check-ins improve communication\n• Track progress with visual dashboards",
                'suggestions': ['View project dashboard', 'Create project templates', 'Schedule team check-ins'],
                'context': 'project_management',
                'intent': 'project_management'
            }
        else:
            return {
                'response': "Ready to start your first project? Here's how to get started:\n\n• Define clear project goals and scope\n• Break down work into manageable tasks\n• Set realistic timelines and milestones\n• Identify team members and roles",
                'suggestions': ['Create first project', 'Learn project planning', 'Set up project templates'],
                'context': 'project_management',
                'intent': 'project_management'
            }
    
    @classmethod
    def _generate_contextual_response(cls, message: str, user, user_context: Dict, chat_context: List[str]) -> Dict[str, Any]:
        """Generate contextual response based on user's current state."""
        recent_projects = user_context.get('recent_projects', [])
        recent_tasks = user_context.get('recent_tasks', [])
        
        if recent_projects:
            project_names = [p['name'] for p in recent_projects[:3]]
            return {
                'response': f"I see you've been working on projects like {', '.join(project_names)}. How can I help you with these projects or something new?",
                'suggestions': ['View project details', 'Create new project', 'Manage project tasks'],
                'context': 'project_context',
                'intent': 'general'
            }
        elif recent_tasks:
            return {
                'response': "I notice you have some tasks assigned. Would you like help organizing them, setting priorities, or creating new ones?",
                'suggestions': ['View my tasks', 'Create new task', 'Organize task list'],
                'context': 'task_context',
                'intent': 'general'
            }
        else:
            return {
                'response': "Welcome to Inspora! I'm here to help you get started. What would you like to do first?",
                'suggestions': ['Create your first project', 'Set up a team', 'Learn the basics'],
                'context': 'welcome',
                'intent': 'general'
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
