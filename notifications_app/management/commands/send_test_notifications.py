"""
Management command to send test notifications.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notifications_app.services import NotificationService
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Send test notifications to demonstrate the notification system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username to send test notifications to'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['all', 'signin', 'task', 'project', 'goal', 'comment', 'mention', 'reminder'],
            default='all',
            help='Type of test notification to send'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=1,
            help='Number of test notifications to send'
        )

    def handle(self, *args, **options):
        username = options['user']
        notification_type = options['type']
        count = options['count']

        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User "{username}" not found')
                )
                return
        else:
            # Get the first user if no username specified
            user = User.objects.first()
            if not user:
                self.stdout.write(
                    self.style.ERROR('No users found in the system')
                )
                return

        self.stdout.write(
            self.style.SUCCESS(f'Sending {count} test notification(s) to user "{user.username}"')
        )

        for i in range(count):
            if notification_type == 'all' or notification_type == 'signin':
                self._send_signin_notification(user, i + 1)

            if notification_type == 'all' or notification_type == 'task':
                self._send_task_notification(user, i + 1)

            if notification_type == 'all' or notification_type == 'project':
                self._send_project_notification(user, i + 1)

            if notification_type == 'all' or notification_type == 'goal':
                self._send_goal_notification(user, i + 1)

            if notification_type == 'all' or notification_type == 'comment':
                self._send_comment_notification(user, i + 1)

            if notification_type == 'all' or notification_type == 'mention':
                self._send_mention_notification(user, i + 1)

            if notification_type == 'all' or notification_type == 'reminder':
                self._send_reminder_notification(user, i + 1)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully sent test notifications to "{user.username}"')
        )

    def _send_signin_notification(self, user, index):
        """Send test signin notification."""
        notification = NotificationService.send_signin_notification(
            user=user,
            ip_address='192.168.1.100',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        if notification:
            self.stdout.write(f'  ✓ Sent signin notification #{index}')

    def _send_task_notification(self, user, index):
        """Send test task completion notification."""
        # Create a mock task object
        class MockTask:
            def __init__(self, task_id, title, project_name):
                self.id = task_id
                self.title = title
                self.project = MockProject(project_name)

        class MockProject:
            def __init__(self, name):
                self.name = name

        mock_task = MockTask(index, f'Test Task {index}', f'Test Project {index}')
        
        notification = NotificationService.send_task_completion_notification(
            task=mock_task,
            completed_by=user
        )
        if notification:
            self.stdout.write(f'  ✓ Sent task completion notification #{index}')

    def _send_project_notification(self, user, index):
        """Send test project completion notification."""
        # Create a mock project object
        class MockProject:
            def __init__(self, project_id, name, description):
                self.id = project_id
                self.name = name
                self.description = description
                self.created_at = timezone.now()
                self.updated_at = timezone.now()

        mock_project = MockProject(index, f'Test Project {index}', f'This is test project {index}')
        
        notification = NotificationService.send_project_completion_notification(
            project=mock_project,
            completed_by=user
        )
        if notification:
            self.stdout.write(f'  ✓ Sent project completion notification #{index}')

    def _send_goal_notification(self, user, index):
        """Send test goal completion notification."""
        # Create a mock goal object
        class MockGoal:
            def __init__(self, goal_id, title, description):
                self.id = goal_id
                self.title = title
                self.description = description

        mock_goal = MockGoal(index, f'Test Goal {index}', f'This is test goal {index}')
        
        notification = NotificationService.send_goal_completion_notification(
            goal=mock_goal,
            completed_by=user
        )
        if notification:
            self.stdout.write(f'  ✓ Sent goal completion notification #{index}')

    def _send_comment_notification(self, user, index):
        """Send test comment notification."""
        notification = NotificationService.create_notification(
            recipient=user,
            notification_type='comment_added',
            title=f'New Comment on Test Item {index}',
            message=f'Someone commented on test item {index}. This is a test comment notification.',
            sender=user,
            priority='normal',
            data={'test': True, 'index': index}
        )
        if notification:
            self.stdout.write(f'  ✓ Sent comment notification #{index}')

    def _send_mention_notification(self, user, index):
        """Send test mention notification."""
        notification = NotificationService.create_notification(
            recipient=user,
            notification_type='mention',
            title=f'You were mentioned in Test Item {index}',
            message=f'Someone mentioned you in test item {index}. This is a test mention notification.',
            sender=user,
            priority='normal',
            data={'test': True, 'index': index}
        )
        if notification:
            self.stdout.write(f'  ✓ Sent mention notification #{index}')

    def _send_reminder_notification(self, user, index):
        """Send test reminder notification."""
        notification = NotificationService.create_notification(
            recipient=user,
            notification_type='reminder',
            title=f'Test Reminder {index}',
            message=f'This is test reminder {index}. Remember to complete your test tasks!',
            sender=user,
            priority='normal',
            data={'test': True, 'index': index}
        )
        if notification:
            self.stdout.write(f'  ✓ Sent reminder notification #{index}')





