"""
Django signals for automatic notifications.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from .models import Notification
from .services import NotificationService
import logging

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def send_signin_notification(sender, request, user, **kwargs):
    """Send notification when user signs in."""
    try:
        # Get client IP address
        ip_address = None
        if request:
            # Get IP from various headers (for proxy/load balancer setups)
            ip_address = (
                request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or
                request.META.get('HTTP_X_REAL_IP') or
                request.META.get('REMOTE_ADDR')
            )
        
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT') if request else None
        
        # Send signin notification
        NotificationService.send_signin_notification(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logger.info(f"Signin notification sent for user {user.username}")
        
    except Exception as e:
        logger.error(f"Error sending signin notification for user {user.username}: {e}")


# Task completion signals
@receiver(post_save, sender='tasks.Task')
def handle_task_completion(sender, instance, created, **kwargs):
    """Handle task completion notifications."""
    try:
        # Check if task was just completed
        if not created and hasattr(instance, 'status'):
            # Get the previous status from the instance
            # Note: This is a simplified approach. For better tracking, use django-simple-history
            if instance.status == 'completed':
                # Send completion notification
                NotificationService.send_task_completion_notification(
                    task=instance,
                    completed_by=instance.assigned_to or instance.created_by
                )
                
                logger.info(f"Task completion notification sent for task {instance.id}")
                
    except Exception as e:
        logger.error(f"Error handling task completion notification: {e}")


# Project completion signals
@receiver(post_save, sender='projects.Project')
def handle_project_completion(sender, instance, created, **kwargs):
    """Handle project completion notifications."""
    try:
        # Check if project was just completed
        if not created and hasattr(instance, 'status'):
            if instance.status == 'completed':
                # Send completion notification
                NotificationService.send_project_completion_notification(
                    project=instance,
                    completed_by=instance.owner or instance.created_by
                )
                
                logger.info(f"Project completion notification sent for project {instance.id}")
                
    except Exception as e:
        logger.error(f"Error handling project completion notification: {e}")


# Goal completion signals
@receiver(post_save, sender='goals.Goal')
def handle_goal_completion(sender, instance, created, **kwargs):
    """Handle goal completion notifications."""
    try:
        # Check if goal was just completed
        if not created and hasattr(instance, 'status'):
            if instance.status == 'completed':
                # Send completion notification
                NotificationService.send_goal_completion_notification(
                    goal=instance,
                    completed_by=instance.user or instance.created_by
                )
                
                logger.info(f"Goal completion notification sent for goal {instance.id}")
                
    except Exception as e:
        logger.error(f"Error handling goal completion notification: {e}")


# Comment notifications
@receiver(post_save, sender='tasks.TaskComment')
def handle_task_comment_notification(sender, instance, created, **kwargs):
    """Handle task comment notifications."""
    if created:
        try:
            # Get the task this comment belongs to
            task = instance.task
            
            if task:
                # Determine who to notify
                recipients = []
                
                if hasattr(task, 'assigned_to') and task.assigned_to:
                    recipients.append(task.assigned_to)
                if hasattr(task, 'created_by'):
                    recipients.append(task.created_by)
                
                # Send notifications to recipients (excluding comment author)
                for recipient in recipients:
                    if recipient != instance.author:
                        title = "New Comment on Task"
                        message = f"{instance.author.get_full_name() or instance.author.username} commented on task '{task.title}'"
                        
                        NotificationService.create_notification(
                            recipient=recipient,
                            notification_type='comment_added',
                            title=title,
                            message=message,
                            sender=instance.author,
                            related_object=task,
                            priority='normal',
                            action_url=task.get_absolute_url() if hasattr(task, 'get_absolute_url') else None
                        )
                
                logger.info(f'Task comment notification sent for comment {instance.id}')
                
        except Exception as e:
            logger.error(f'Error handling task comment notification: {e}')


@receiver(post_save, sender='goals.GoalComment')
def handle_goal_comment_notification(sender, instance, created, **kwargs):
    """Handle goal comment notifications."""
    if created:
        try:
            # Get the goal this comment belongs to
            goal = instance.goal
            
            if goal:
                # Determine who to notify
                recipients = []
                
                if hasattr(goal, 'user'):
                    recipients.append(goal.user)
                if hasattr(goal, 'created_by'):
                    recipients.append(goal.created_by)
                
                # Send notifications to recipients (excluding comment author)
                for recipient in recipients:
                    if recipient != instance.author:
                        title = "New Comment on Goal"
                        message = f"{instance.author.get_full_name() or instance.author.username} commented on goal '{goal.title}'"
                        
                        NotificationService.create_notification(
                            recipient=recipient,
                            notification_type='comment_added',
                            title=title,
                            message=message,
                            sender=instance.author,
                            related_object=goal,
                            priority='normal',
                            action_url=goal.get_absolute_url() if hasattr(goal, 'get_absolute_url') else None
                        )
                
                logger.info(f'Goal comment notification sent for comment {instance.id}')
                
        except Exception as e:
            logger.error(f'Error handling goal comment notification: {e}')


# Mention notifications in task comments
@receiver(post_save, sender='tasks.TaskComment')
def handle_task_mention_notification(sender, instance, created, **kwargs):
    """Handle mention notifications in task comments."""
    if created and instance.content:
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Simple mention detection (you can enhance this with regex)
            content = instance.content.lower()
            mentioned_users = []
            
            # Check for @username mentions
            for user in User.objects.all():
                if f"@{user.username.lower()}" in content:
                    mentioned_users.append(user)
            
            # Send mention notifications
            for mentioned_user in mentioned_users:
                if mentioned_user != instance.author:
                    title = "You were mentioned in a task comment"
                    message = f"{instance.author.get_full_name() or instance.author.username} mentioned you in a comment on task '{instance.task.title}'"
                    
                    NotificationService.create_notification(
                        recipient=mentioned_user,
                        notification_type='mention',
                        title=title,
                        message=message,
                        sender=instance.author,
                        related_object=instance.task,
                        priority='normal',
                        action_url=instance.task.get_absolute_url() if hasattr(instance.task, 'get_absolute_url') else None
                    )
            
            if mentioned_users:
                logger.info(f'Task mention notifications sent for comment {instance.id}')
                
        except Exception as e:
            logger.error(f'Error handling task mention notification: {e}')


# Mention notifications in goal comments
@receiver(post_save, sender='goals.GoalComment')
def handle_goal_mention_notification(sender, instance, created, **kwargs):
    """Handle mention notifications in goal comments."""
    if created and instance.content:
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Simple mention detection (you can enhance this with regex)
            content = instance.content.lower()
            mentioned_users = []
            
            # Check for @username mentions
            for user in User.objects.all():
                if f"@{user.username.lower()}" in content:
                    mentioned_users.append(user)
            
            # Send mention notifications
            for mentioned_user in mentioned_users:
                if mentioned_user != instance.author:
                    title = "You were mentioned in a goal comment"
                    message = f"{instance.author.get_full_name() or instance.author.username} mentioned you in a comment on goal '{instance.goal.title}'"
                    
                    NotificationService.create_notification(
                        recipient=mentioned_user,
                        notification_type='mention',
                        title=title,
                        message=message,
                        sender=instance.author,
                        related_object=instance.goal,
                        priority='normal',
                        action_url=instance.goal.get_absolute_url() if hasattr(instance.goal, 'get_absolute_url') else None
                    )
            
            if mentioned_users:
                logger.info(f'Goal mention notifications sent for comment {instance.id}')
                
        except Exception as e:
            logger.error(f'Error handling goal mention notification: {e}')


# Task assignment notifications
@receiver(post_save, sender='tasks.Task')
def handle_task_assignment(sender, instance, created, **kwargs):
    """Handle task assignment notifications."""
    try:
        # Check if task was just assigned or reassigned
        if hasattr(instance, 'assigned_to') and instance.assigned_to:
            # For new tasks or reassigned tasks
            if created or (hasattr(instance, '_state') and instance._state.adding is False):
                # Check if this is a reassignment
                if hasattr(instance, '_state') and not instance._state.adding:
                    # This is an update, check if assigned_to changed
                    try:
                        old_instance = sender.objects.get(pk=instance.pk)
                        if old_instance.assigned_to != instance.assigned_to:
                            # Task was reassigned
                            title = "Task Reassigned to You"
                            message = f"The task '{instance.title}' has been reassigned to you"
                            
                            NotificationService.create_notification(
                                recipient=instance.assigned_to,
                                notification_type='task_assigned',
                                title=title,
                                message=message,
                                sender=instance.created_by,
                                related_object=instance,
                                priority='normal',
                                action_url=instance.get_absolute_url() if hasattr(instance, 'get_absolute_url') else None
                            )
                            
                            logger.info(f"Task reassignment notification sent for task {instance.id}")
                    except sender.DoesNotExist:
                        pass
                else:
                    # New task assignment
                    title = "New Task Assigned"
                    message = f"You have been assigned a new task: '{instance.title}'"
                    
                    NotificationService.create_notification(
                        recipient=instance.assigned_to,
                        notification_type='task_assigned',
                        title=title,
                        message=message,
                        sender=instance.created_by,
                        related_object=instance,
                        priority='normal',
                        action_url=instance.get_absolute_url() if hasattr(instance, 'get_absolute_url') else None
                    )
                    
                    logger.info(f"Task assignment notification sent for task {instance.id}")
                    
    except Exception as e:
        logger.error(f"Error handling task assignment notification: {e}")


# Project deadline notifications
@receiver(post_save, sender='projects.Project')
def handle_project_deadline(sender, instance, created, **kwargs):
    """Handle project deadline notifications."""
    try:
        if hasattr(instance, 'deadline') and instance.deadline:
            from datetime import timedelta
            
            # Check if deadline is approaching (within 3 days)
            now = timezone.now().date()
            days_until_deadline = (instance.deadline - now).days
            
            if 0 <= days_until_deadline <= 3:
                # Send deadline reminder
                if days_until_deadline == 0:
                    title = "Project Deadline Today! ⚠️"
                    message = f"Your project '{instance.name}' is due today!"
                    priority = 'urgent'
                elif days_until_deadline == 1:
                    title = "Project Deadline Tomorrow! ⚠️"
                    message = f"Your project '{instance.name}' is due tomorrow!"
                    priority = 'high'
                else:
                    title = "Project Deadline Approaching"
                    message = f"Your project '{instance.name}' is due in {days_until_deadline} days"
                    priority = 'normal'
                
                NotificationService.create_notification(
                    recipient=instance.owner,
                    notification_type='reminder',
                    title=title,
                    message=message,
                    sender=None,
                    related_object=instance,
                    priority=priority,
                    action_url=instance.get_absolute_url() if hasattr(instance, 'get_absolute_url') else None
                )
                
                logger.info(f"Project deadline notification sent for project {instance.id}")
                
    except Exception as e:
        logger.error(f"Error handling project deadline notification: {e}")


# Task deadline notifications
@receiver(post_save, sender='tasks.Task')
def handle_task_deadline(sender, instance, created, **kwargs):
    """Handle task deadline notifications."""
    try:
        if hasattr(instance, 'due_date') and instance.due_date:
            from datetime import timedelta
            
            # Check if deadline is approaching (within 2 days)
            now = timezone.now().date()
            days_until_deadline = (instance.due_date - now).days
            
            if 0 <= days_until_deadline <= 2:
                # Send deadline reminder
                if days_until_deadline == 0:
                    title = "Task Due Today! ⚠️"
                    message = f"Your task '{instance.title}' is due today!"
                    priority = 'urgent'
                elif days_until_deadline == 1:
                    title = "Task Due Tomorrow! ⚠️"
                    message = f"Your task '{instance.title}' is due tomorrow!"
                    priority = 'high'
                else:
                    title = "Task Deadline Approaching"
                    message = f"Your task '{instance.title}' is due in {days_until_deadline} days"
                    priority = 'normal'
                
                if instance.assigned_to:
                    NotificationService.create_notification(
                        recipient=instance.assigned_to,
                        notification_type='reminder',
                        title=title,
                        message=message,
                        sender=None,
                        related_object=instance,
                        priority=priority,
                        action_url=instance.get_absolute_url() if hasattr(instance, 'get_absolute_url') else None
                    )
                    
                    logger.info(f"Task deadline notification sent for task {instance.id}")
                    
    except Exception as e:
        logger.error(f"Error handling task deadline notification: {e}")


# Overdue task notifications
@receiver(post_save, sender='tasks.Task')
def handle_overdue_task(sender, instance, created, **kwargs):
    """Handle overdue task notifications."""
    try:
        if hasattr(instance, 'due_date') and instance.due_date:
            now = timezone.now().date()
            
            # Check if task is overdue
            if instance.due_date < now and instance.status not in ['completed', 'cancelled']:
                title = "Task Overdue! ⚠️"
                message = f"Your task '{instance.title}' is overdue by {(now - instance.due_date).days} days"
                
                if instance.assigned_to:
                    NotificationService.create_notification(
                        recipient=instance.assigned_to,
                        notification_type='task_overdue',
                        title=title,
                        message=message,
                        sender=None,
                        related_object=instance,
                        priority='high',
                        action_url=instance.get_absolute_url() if hasattr(instance, 'get_absolute_url') else None
                    )
                    
                    logger.info(f"Overdue task notification sent for task {instance.id}")
                    
    except Exception as e:
        logger.error(f"Error handling overdue task notification: {e}")


# Team member addition notifications
@receiver(post_save, sender='accounts.TeamMembership')
def handle_team_member_addition(sender, instance, created, **kwargs):
    """Handle team member addition notifications."""
    if created:
        try:
            title = "Welcome to the Team! 👋"
            message = f"You have been added to the team '{instance.team.name}' as a {instance.get_role_display()}"
            
            NotificationService.create_notification(
                recipient=instance.user,
                notification_type='system',
                title=title,
                message=message,
                sender=instance.team.created_by,
                related_object=instance.team,
                priority='normal',
                action_url=instance.team.get_absolute_url() if hasattr(instance.team, 'get_absolute_url') else None
            )
            
            logger.info(f"Team member addition notification sent for user {instance.user.username}")
            
        except Exception as e:
            logger.error(f"Error handling team member addition notification: {e}")


# Clean up old notifications
@receiver(post_save, sender=Notification)
def cleanup_old_notifications(sender, instance, **kwargs):
    """Clean up old notifications periodically."""
    try:
        # This could be moved to a management command or Celery task
        # For now, we'll do it here occasionally
        if instance.id % 100 == 0:  # Every 100th notification
            NotificationService.delete_old_notifications(days=30)
            
    except Exception as e:
        logger.error(f"Error cleaning up old notifications: {e}")
