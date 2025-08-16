"""
Notification services for Inspora platform.
Handles creating and sending simple text-based notifications.
"""
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.db.models import Q
from .models import Notification, NotificationTemplate, NotificationChannel, NotificationPreference
import json
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class NotificationService:
    """Main service for handling simple text notifications."""
    
    @classmethod
    def create_notification(cls, recipient, notification_type, title, message, 
                          sender=None, related_object=None, priority='normal', 
                          data=None, action_url=None):
        """Create a new simple text notification."""
        try:
            # Get or create notification preferences
            preferences, created = NotificationPreference.objects.get_or_create(
                user=recipient,
                defaults={
                    'email_notifications': True,
                    'push_notifications': True,
                    'in_app_notifications': True,
                    'sms_notifications': False,
                }
            )
            
            # Check if user wants this type of notification
            if not cls._should_send_notification(recipient, notification_type, preferences):
                return None
            
            # Check quiet hours
            if preferences.is_quiet_hours():
                logger.info(f"Notification for {recipient.username} delayed due to quiet hours")
                # Store for later delivery
                return cls._create_delayed_notification(
                    recipient, notification_type, title, message, 
                    sender, related_object, priority, data, action_url
                )
            
            # Create notification
            notification = Notification.objects.create(
                recipient=recipient,
                sender=sender,
                notification_type=notification_type,
                title=title,
                message=message,
                priority=priority,
                data=data or {},
                action_url=action_url,
                content_type=ContentType.objects.get_for_model(related_object) if related_object else None,
                object_id=related_object.id if related_object else None,
            )
            
            # Send notification through all active channels
            cls._send_notification_channels(notification, preferences)
            
            return notification
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return None
    
    @classmethod
    def _should_send_notification(cls, user, notification_type, preferences):
        """Check if user should receive this notification type."""
        if notification_type == 'task_completed' and not preferences.task_notifications:
            return False
        elif notification_type == 'project_update' and not preferences.project_notifications:
            return False
        elif notification_type == 'goal_update' and not preferences.goal_notifications:
            return False
        elif notification_type == 'comment_added' and not preferences.comment_notifications:
            return False
        elif notification_type == 'mention' and not preferences.mention_notifications:
            return False
        elif notification_type == 'system' and not preferences.system_notifications:
            return False
        
        return True
    
    @classmethod
    def _create_delayed_notification(cls, recipient, notification_type, title, message,
                                   sender, related_object, priority, data, action_url):
        """Create notification for delayed delivery."""
        # Store in data for later processing
        delayed_data = {
            'delayed': True,
            'original_type': notification_type,
            'original_title': title,
            'original_message': message,
            'original_priority': priority,
            'original_data': data or {},
            'original_action_url': action_url,
            'delayed_at': timezone.now().isoformat(),
        }
        
        return Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type='reminder',
            title='Delayed Notification',
            message='You have pending notifications',
            priority=priority,
            data=delayed_data,
            action_url=None,
            content_type=ContentType.objects.get_for_model(related_object) if related_object else None,
            object_id=related_object.id if related_object else None,
        )
    
    @classmethod
    def _send_notification_channels(cls, notification, preferences):
        """Send simple text notification through all active channels."""
        channels = NotificationChannel.objects.filter(is_active=True)
        
        for channel in channels:
            try:
                if channel.channel_type == 'email' and preferences.email_notifications:
                    channel.send_notification(notification, notification.data)
                elif channel.channel_type == 'push' and preferences.push_notifications:
                    channel.send_notification(notification, notification.data)
                elif channel.channel_type == 'in_app' and preferences.in_app_notifications:
                    channel.send_notification(notification, notification.data)
                elif channel.channel_type == 'sms' and preferences.sms_notifications:
                    channel.send_notification(notification, notification.data)
                
                # Mark as sent
                notification.mark_as_sent()
                
            except Exception as e:
                logger.error(f"Error sending notification through {channel.name}: {e}")
    
    @classmethod
    def send_signin_notification(cls, user, ip_address=None, user_agent=None):
        """Send simple text notification when user signs in."""
        try:
            # Get location info (you can enhance this with IP geolocation)
            location_info = "Unknown location"
            if ip_address:
                location_info = f"IP: {ip_address}"
            
            title = "New Sign In Detected"
            message = f"Welcome back! You've successfully signed in to Inspora from {location_info}."
            
            # Add security info
            data = {
                'signin_time': timezone.now().isoformat(),
                'ip_address': ip_address,
                'user_agent': user_agent,
                'location': location_info,
                'device_type': cls._detect_device_type(user_agent) if user_agent else 'Unknown'
            }
            
            # Create notification
            notification = cls.create_notification(
                recipient=user,
                notification_type='system',
                title=title,
                message=message,
                priority='normal',
                data=data,
                action_url=reverse('accounts:profile')
            )
            
            # Also send to admin if it's a suspicious login
            if cls._is_suspicious_login(user, ip_address, user_agent):
                cls._send_suspicious_login_alert(user, ip_address, user_agent)
            
            return notification
            
        except Exception as e:
            logger.error(f"Error sending signin notification: {e}")
            return None
    
    @classmethod
    def send_task_completion_notification(cls, task, completed_by):
        """Send simple text notification when task is completed."""
        try:
            # Get task details
            task_title = task.title
            project_name = task.project.name if hasattr(task, 'project') and task.project else "No Project"
            
            title = "Task Completed! 🎉"
            message = f"Great job! You've completed the task '{task_title}' in project '{project_name}'."
            
            data = {
                'task_id': task.id,
                'task_title': task_title,
                'project_name': project_name,
                'completed_at': timezone.now().isoformat(),
                'completed_by': completed_by.username,
                'task_priority': getattr(task, 'priority', 'Normal'),
                'task_due_date': task.due_date.isoformat() if hasattr(task, 'due_date') and task.due_date else None
            }
            
            # Create notification for task owner
            notification = cls.create_notification(
                recipient=completed_by,
                notification_type='task_completed',
                title=title,
                message=message,
                sender=completed_by,
                related_object=task,
                priority='normal',
                data=data,
                action_url=reverse('tasks:task_detail', kwargs={'pk': task.id})
            )
            
            # Notify project manager if different from task owner
            if hasattr(task, 'project') and task.project and task.project.owner != completed_by:
                manager_title = "Team Member Completed Task"
                manager_message = f"{completed_by.get_full_name() or completed_by.username} has completed task '{task_title}' in project '{project_name}'."
                
                cls.create_notification(
                    recipient=task.project.owner,
                    notification_type='task_completed',
                    title=manager_title,
                    message=manager_message,
                    sender=completed_by,
                    related_object=task,
                    priority='normal',
                    data=data,
                    action_url=reverse('tasks:task_detail', kwargs={'pk': task.id})
                )
            
            # Notify team members if task is part of a team project
            if hasattr(task, 'project') and task.project and hasattr(task.project, 'team'):
                cls._notify_team_members(task, completed_by, data)
            
            return notification
            
        except Exception as e:
            logger.error(f"Error sending task completion notification: {e}")
            return None
    
    @classmethod
    def send_project_completion_notification(cls, project, completed_by):
        """Send simple text notification when project is completed."""
        try:
            project_name = project.name
            project_description = getattr(project, 'description', '')
            
            title = "Project Completed! 🚀"
            message = f"Congratulations! The project '{project_name}' has been successfully completed."
            
            data = {
                'project_id': project.id,
                'project_name': project_name,
                'project_description': project_description,
                'completed_at': timezone.now().isoformat(),
                'completed_by': completed_by.username,
                'project_start_date': project.created_at.isoformat() if hasattr(project, 'created_at') else None,
                'project_duration': cls._calculate_project_duration(project)
            }
            
            # Create notification for project owner
            notification = cls.create_notification(
                recipient=completed_by,
                notification_type='project_update',
                title=title,
                message=message,
                sender=completed_by,
                related_object=project,
                priority='high',
                data=data,
                action_url=reverse('projects:project_detail', kwargs={'pk': project.id})
            )
            
            # Notify all team members
            if hasattr(project, 'team') and project.team:
                cls._notify_project_team(project, completed_by, data)
            
            # Notify stakeholders (if any)
            cls._notify_project_stakeholders(project, completed_by, data)
            
            return notification
            
        except Exception as e:
            logger.error(f"Error sending project completion notification: {e}")
            return None
    
    @classmethod
    def send_goal_completion_notification(cls, goal, completed_by):
        """Send simple text notification when goal is completed."""
        try:
            goal_title = goal.title
            goal_description = getattr(goal, 'description', '')
            
            title = "Goal Achieved! 🎯"
            message = f"Fantastic! You've achieved your goal '{goal_title}'. Keep up the great work!"
            
            data = {
                'goal_id': goal.id,
                'goal_title': goal_title,
                'goal_description': goal_description,
                'achieved_at': timezone.now().isoformat(),
                'achieved_by': completed_by.username,
                'goal_deadline': goal.deadline.isoformat() if hasattr(goal, 'deadline') and goal.deadline else None,
                'goal_progress': getattr(goal, 'progress', 100)
            }
            
            notification = cls.create_notification(
                recipient=completed_by,
                notification_type='goal_update',
                title=title,
                message=message,
                sender=completed_by,
                related_object=goal,
                priority='high',
                data=data,
                action_url=reverse('goals:goal_detail', kwargs={'pk': goal.id})
            )
            
            return notification
            
        except Exception as e:
            logger.error(f"Error sending goal completion notification: {e}")
            return None
    
    @classmethod
    def _detect_device_type(cls, user_agent):
        """Detect device type from user agent string."""
        if not user_agent:
            return 'Unknown'
        
        user_agent_lower = user_agent.lower()
        
        if 'mobile' in user_agent_lower or 'android' in user_agent_lower or 'iphone' in user_agent_lower:
            return 'Mobile'
        elif 'tablet' in user_agent_lower or 'ipad' in user_agent_lower:
            return 'Tablet'
        elif 'desktop' in user_agent_lower or 'windows' in user_agent_lower or 'mac' in user_agent_lower:
            return 'Desktop'
        else:
            return 'Unknown'
    
    @classmethod
    def _is_suspicious_login(cls, user, ip_address, user_agent):
        """Check if login is suspicious."""
        # Add your suspicious login detection logic here
        # For example: unusual IP, new device, multiple failed attempts, etc.
        return False
    
    @classmethod
    def _send_suspicious_login_alert(cls, user, ip_address, user_agent):
        """Send alert for suspicious login."""
        # Implementation for suspicious login alerts
        pass
    
    @classmethod
    def _notify_team_members(cls, task, completed_by, data):
        """Notify team members about task completion."""
        try:
            if hasattr(task, 'project') and task.project and hasattr(task.project, 'team'):
                team_members = task.project.team.members.all()
                
                for member in team_members:
                    if member != completed_by:  # Don't notify the person who completed it
                        title = "Team Member Completed Task"
                        message = f"{completed_by.get_full_name() or completed_by.username} has completed task '{task.title}' in project '{task.project.name}'."
                        
                        cls.create_notification(
                            recipient=member,
                            notification_type='task_completed',
                            title=title,
                            message=message,
                            sender=completed_by,
                            related_object=task,
                            priority='normal',
                            data=data,
                            action_url=reverse('tasks:task_detail', kwargs={'pk': task.id})
                        )
        except Exception as e:
            logger.error(f"Error notifying team members: {e}")
    
    @classmethod
    def _notify_project_team(cls, project, completed_by, data):
        """Notify project team about project completion."""
        try:
            if hasattr(project, 'team') and project.team:
                team_members = project.team.members.all()
                
                for member in team_members:
                    if member != completed_by:
                        title = "Project Completed!"
                        message = f"The project '{project.name}' has been completed by {completed_by.get_full_name() or completed_by.username}."
                        
                        cls.create_notification(
                            recipient=member,
                            notification_type='project_update',
                            title=title,
                            message=message,
                            sender=completed_by,
                            related_object=project,
                            priority='normal',
                            data=data,
                            action_url=reverse('projects:project_detail', kwargs={'pk': project.id})
                        )
        except Exception as e:
            logger.error(f"Error notifying project team: {e}")
    
    @classmethod
    def _notify_project_stakeholders(cls, project, completed_by, data):
        """Notify project stakeholders about project completion."""
        # Implementation for stakeholder notifications
        pass
    
    @classmethod
    def _calculate_project_duration(cls, project):
        """Calculate project duration."""
        try:
            if hasattr(project, 'created_at') and hasattr(project, 'updated_at'):
                duration = project.updated_at - project.created_at
                return str(duration.days) + " days"
            return "Unknown"
        except:
            return "Unknown"
    
    @classmethod
    def process_delayed_notifications(cls):
        """Process delayed notifications outside quiet hours."""
        try:
            delayed_notifications = Notification.objects.filter(
                data__delayed=True,
                is_sent=False
            )
            
            for notification in delayed_notifications:
                try:
                    # Get original notification data
                    delayed_data = notification.data
                    original_type = delayed_data.get('original_type')
                    original_title = delayed_data.get('original_title')
                    original_message = delayed_data.get('original_message')
                    original_priority = delayed_data.get('original_priority')
                    original_data = delayed_data.get('original_data', {})
                    original_action_url = delayed_data.get('original_action_url')
                    
                    # Check if still in quiet hours
                    preferences = NotificationPreference.objects.get(user=notification.recipient)
                    if preferences.is_quiet_hours():
                        continue
                    
                    # Update notification with original data
                    notification.notification_type = original_type
                    notification.title = original_title
                    notification.message = original_message
                    notification.priority = original_priority
                    notification.data = original_data
                    notification.action_url = original_action_url
                    notification.save()
                    
                    # Send notification
                    cls._send_notification_channels(notification, preferences)
                    
                except Exception as e:
                    logger.error(f"Error processing delayed notification {notification.id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error processing delayed notifications: {e}")
    
    @classmethod
    def get_user_notifications(cls, user, limit=50, unread_only=False):
        """Get user's simple text notifications."""
        queryset = Notification.objects.filter(recipient=user)
        
        if unread_only:
            queryset = queryset.filter(is_read=False)
        
        return queryset[:limit]
    
    @classmethod
    def mark_notification_read(cls, notification_id, user):
        """Mark notification as read."""
        try:
            notification = Notification.objects.get(id=notification_id, recipient=user)
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False
    
    @classmethod
    def mark_all_notifications_read(cls, user):
        """Mark all user notifications as read."""
        try:
            Notification.objects.filter(recipient=user, is_read=False).update(
                is_read=True,
                read_at=timezone.now()
            )
            return True
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {e}")
            return False
    
    @classmethod
    def delete_old_notifications(cls, days=30):
        """Delete old notifications."""
        try:
            cutoff_date = timezone.now() - timezone.timedelta(days=days)
            deleted_count = Notification.objects.filter(
                created_at__lt=cutoff_date,
                is_read=True,
                is_archived=True
            ).delete()[0]
            
            logger.info(f"Deleted {deleted_count} old notifications")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting old notifications: {e}")
            return 0
