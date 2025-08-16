"""
Views for notifications app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Notification, NotificationPreference
from .services import NotificationService
import json


@login_required
def notification_list(request):
    """List all notifications for the user."""
    notifications = NotificationService.get_user_notifications(
        user=request.user,
        limit=100,
        unread_only=False
    )
    
    context = {
        'notifications': notifications,
        'page_title': 'Notifications'
    }
    
    return render(request, 'notifications_app/notification_list.html', context)


@login_required
def notification_detail(request, pk):
    """Show notification detail."""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    
    # Mark as read when viewed
    notification.mark_as_read()
    
    context = {
        'notification': notification,
        'page_title': notification.title
    }
    
    return render(request, 'notifications_app/notification_detail.html', context)


@login_required
def notification_preferences(request):
    """Manage notification preferences."""
    preferences, created = NotificationPreference.objects.get_or_create(
        user=request.user,
        defaults={
            'email_notifications': True,
            'push_notifications': True,
            'in_app_notifications': True,
            'sms_notifications': False,
        }
    )
    
    if request.method == 'POST':
        # Update preferences
        preferences.email_notifications = request.POST.get('email_notifications') == 'on'
        preferences.push_notifications = request.POST.get('push_notifications') == 'on'
        preferences.in_app_notifications = request.POST.get('in_app_notifications') == 'on'
        preferences.sms_notifications = request.POST.get('sms_notifications') == 'on'
        
        preferences.task_notifications = request.POST.get('task_notifications') == 'on'
        preferences.project_notifications = request.POST.get('project_notifications') == 'on'
        preferences.goal_notifications = request.POST.get('goal_notifications') == 'on'
        preferences.comment_notifications = request.POST.get('comment_notifications') == 'on'
        preferences.mention_notifications = request.POST.get('mention_notifications') == 'on'
        preferences.system_notifications = request.POST.get('system_notifications') == 'on'
        
        preferences.notification_frequency = request.POST.get('notification_frequency', 'immediate')
        preferences.quiet_hours_enabled = request.POST.get('quiet_hours_enabled') == 'on'
        
        # Handle quiet hours
        if preferences.quiet_hours_enabled:
            try:
                preferences.quiet_hours_start = request.POST.get('quiet_hours_start')
                preferences.quiet_hours_end = request.POST.get('quiet_hours_end')
            except:
                pass
        
        preferences.save()
        
        return redirect('notifications_app:preferences')
    
    context = {
        'preferences': preferences,
        'page_title': 'Notification Preferences'
    }
    
    return render(request, 'notifications_app/preferences.html', context)


# API Views for AJAX requests
@login_required
@require_http_methods(["GET"])
def api_unread_notifications(request):
    """Get unread notifications count and list."""
    try:
        notifications = NotificationService.get_user_notifications(
            user=request.user,
            limit=10,
            unread_only=True
        )
        
        # Convert to JSON-serializable format
        notification_data = []
        for notification in notifications:
            notification_data.append({
                'id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'notification_type': notification.notification_type,
                'priority': notification.priority,
                'created_at': notification.created_at.isoformat(),
                'action_url': notification.action_url,
                'is_read': notification.is_read,
            })
        
        return JsonResponse({
            'success': True,
            'count': len(notification_data),
            'notifications': notification_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_mark_notification_read(request, notification_id):
    """Mark a notification as read."""
    try:
        success = NotificationService.mark_notification_read(
            notification_id=notification_id,
            user=request.user
        )
        
        if success:
            return JsonResponse({'success': True})
        else:
            return JsonResponse({
                'success': False,
                'error': 'Notification not found or already read'
            }, status=404)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_mark_all_read(request):
    """Mark all notifications as read."""
    try:
        success = NotificationService.mark_all_notifications_read(user=request.user)
        
        if success:
            return JsonResponse({'success': True})
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to mark notifications as read'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_notification_stats(request):
    """Get notification statistics for the user."""
    try:
        total_notifications = Notification.objects.filter(recipient=request.user).count()
        unread_notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        # Get notifications by type
        type_counts = {}
        for notification_type, _ in Notification.NOTIFICATION_TYPES:
            count = Notification.objects.filter(
                recipient=request.user,
                notification_type=notification_type
            ).count()
            type_counts[notification_type] = count
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total': total_notifications,
                'unread': unread_notifications,
                'by_type': type_counts
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_test_notification(request):
    """Send a test notification to the user."""
    try:
        # Create a test notification
        notification = NotificationService.create_notification(
            recipient=request.user,
            notification_type='system',
            title='Test Notification',
            message='This is a test notification to verify your notification settings.',
            priority='normal',
            data={'test': True}
        )
        
        if notification:
            return JsonResponse({
                'success': True,
                'message': 'Test notification sent successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to send test notification'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["DELETE"])
def api_delete_notification(request, notification_id):
    """Delete a notification."""
    try:
        notification = get_object_or_404(Notification, pk=notification_id, recipient=request.user)
        notification.delete()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_archive_notification(request, notification_id):
    """Archive a notification."""
    try:
        notification = get_object_or_404(Notification, pk=notification_id, recipient=request.user)
        notification.is_archived = True
        notification.save()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_notification_preferences(request):
    """Get user notification preferences."""
    try:
        preferences, created = NotificationPreference.objects.get_or_create(
            user=request.user,
            defaults={
                'email_notifications': True,
                'push_notifications': True,
                'in_app_notifications': True,
                'sms_notifications': False,
            }
        )
        
        return JsonResponse({
            'success': True,
            'preferences': {
                'email_notifications': preferences.email_notifications,
                'push_notifications': preferences.push_notifications,
                'in_app_notifications': preferences.in_app_notifications,
                'sms_notifications': preferences.sms_notifications,
                'task_notifications': preferences.task_notifications,
                'project_notifications': preferences.project_notifications,
                'goal_notifications': preferences.goal_notifications,
                'comment_notifications': preferences.comment_notifications,
                'mention_notifications': preferences.mention_notifications,
                'system_notifications': preferences.system_notifications,
                'notification_frequency': preferences.notification_frequency,
                'quiet_hours_enabled': preferences.quiet_hours_enabled,
                'quiet_hours_start': preferences.quiet_hours_start.isoformat() if preferences.quiet_hours_start else None,
                'quiet_hours_end': preferences.quiet_hours_end.isoformat() if preferences.quiet_hours_end else None,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_update_preferences(request):
    """Update user notification preferences."""
    try:
        data = json.loads(request.body)
        preferences, created = NotificationPreference.objects.get_or_create(
            user=request.user,
            defaults={
                'email_notifications': True,
                'push_notifications': True,
                'in_app_notifications': True,
                'sms_notifications': False,
            }
        )
        
        # Update preferences from JSON data
        for field, value in data.items():
            if hasattr(preferences, field):
                setattr(preferences, field, value)
        
        preferences.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Preferences updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

