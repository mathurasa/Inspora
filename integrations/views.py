"""
Integration views for Inspora platform.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from .models import Integration, GoogleDriveIntegration, IntegrationLog
from .google_drive import GoogleDriveService
import json


@login_required
def integration_hub(request):
    """Integration Hub main view."""
    integrations = Integration.objects.filter(created_by=request.user, is_active=True)
    
    # Get integration statistics
    connected_count = integrations.filter(status='connected').count()
    total_count = integrations.count()
    
    context = {
        'integrations': integrations,
        'connected_count': connected_count,
        'total_count': total_count,
        'available_integrations': Integration.INTEGRATION_TYPES,
    }
    
    return render(request, 'integrations/integration_hub.html', context)


@login_required
def google_drive_connect(request):
    """Connect Google Drive integration."""
    if request.method == 'POST':
        try:
            # Check if Google OAuth2 is configured
            if not settings.GOOGLE_OAUTH2_CLIENT_ID or not settings.GOOGLE_OAUTH2_CLIENT_SECRET:
                messages.error(request, 'Google OAuth2 is not configured. Please contact administrator.')
                return redirect('integrations:integration_hub')
            
            # Create or get integration
            integration, created = Integration.objects.get_or_create(
                created_by=request.user,
                integration_type='google_drive',
                defaults={
                    'name': 'Google Drive',
                    'status': 'connecting',
                    'config': {
                        'scopes': ['https://www.googleapis.com/auth/drive'],
                        'redirect_uri': settings.GOOGLE_OAUTH2_REDIRECT_URI
                    }
                }
            )
            
            if not created:
                integration.status = 'connecting'
                integration.save()
            
            # Redirect to Google OAuth2
            from accounts.google_auth import get_google_oauth2_url
            auth_url = get_google_oauth2_url()
            return redirect(auth_url)
            
        except Exception as e:
            messages.error(request, f'Failed to connect Google Drive: {str(e)}')
            return redirect('integrations:integration_hub')
    
    return redirect('integrations:integration_hub')


@login_required
def google_drive_callback(request):
    """Handle Google Drive OAuth2 callback."""
    try:
        # Get authorization code from callback
        code = request.GET.get('code')
        if not code:
            messages.error(request, 'Authorization code not received from Google.')
            return redirect('integrations:integration_hub')
        
        # Exchange code for access token
        from accounts.google_auth import exchange_code_for_token
        token_data = exchange_code_for_token(code)
        
        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token')
        
        if not access_token:
            messages.error(request, 'Failed to get access token from Google.')
            return redirect('integrations:integration_hub')
        
        # Get user information from Google
        from accounts.google_auth import get_user_info_from_token
        user_info = get_user_info_from_token(access_token)
        
        # Update or create Google Drive integration
        integration = Integration.objects.get(
            created_by=request.user,
            integration_type='google_drive'
        )
        
        # Create or update Google Drive integration details
        drive_integration, created = GoogleDriveIntegration.objects.get_or_create(
            integration=integration,
            defaults={
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_expiry': timezone.now() + timezone.timedelta(seconds=token_data.get('expires_in', 3600))
            }
        )
        
        if not created:
            drive_integration.access_token = access_token
            drive_integration.refresh_token = refresh_token
            drive_integration.token_expiry = timezone.now() + timezone.timedelta(seconds=token_data.get('expires_in', 3600))
            drive_integration.save()
        
        # Update integration status
        integration.status = 'connected'
        integration.last_sync = timezone.now()
        integration.save()
        
        # Test connection
        try:
            drive_service = GoogleDriveService(drive_integration)
            if drive_service.test_connection():
                messages.success(request, 'Google Drive connected successfully!')
            else:
                messages.warning(request, 'Google Drive connected but connection test failed.')
        except Exception as e:
            messages.warning(request, f'Google Drive connected but connection test failed: {str(e)}')
        
        return redirect('integrations:integration_hub')
        
    except Exception as e:
        messages.error(request, f'Failed to connect Google Drive: {str(e)}')
        return redirect('integrations:integration_hub')


@login_required
def google_drive_disconnect(request):
    """Disconnect Google Drive integration."""
    try:
        integration = get_object_or_404(
            Integration,
            created_by=request.user,
            integration_type='google_drive'
        )
        
        # Delete Google Drive integration details
        if hasattr(integration, 'google_drive'):
            integration.google_drive.delete()
        
        # Update integration status
        integration.status = 'disconnected'
        integration.save()
        
        messages.success(request, 'Google Drive disconnected successfully.')
        
    except Exception as e:
        messages.error(request, f'Failed to disconnect Google Drive: {str(e)}')
    
    return redirect('integrations:integration_hub')


@login_required
def google_drive_files(request):
    """List Google Drive files."""
    try:
        integration = get_object_or_404(
            Integration,
            created_by=request.user,
            integration_type='google_drive',
            status='connected'
        )
        
        drive_integration = integration.google_drive
        
        # Get folder ID from query params
        folder_id = request.GET.get('folder_id')
        
        # Get files from Google Drive
        drive_service = GoogleDriveService(drive_integration)
        files = drive_service.list_files(folder_id=folder_id)
        
        context = {
            'files': files,
            'current_folder_id': folder_id,
            'integration': integration
        }
        
        return render(request, 'integrations/google_drive_files.html', context)
        
    except Exception as e:
        messages.error(request, f'Failed to load Google Drive files: {str(e)}')
        return redirect('integrations:integration_hub')


@login_required
def google_drive_upload(request):
    """Upload file to Google Drive."""
    if request.method == 'POST':
        try:
            integration = get_object_or_404(
                Integration,
                created_by=request.user,
                integration_type='google_drive',
                status='connected'
            )
            
            drive_integration = integration.google_drive
            
            # Get uploaded file
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return JsonResponse({'error': 'No file uploaded'}, status=400)
            
            # Get folder ID
            folder_id = request.POST.get('folder_id')
            
            # Save file temporarily
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            try:
                # Upload to Google Drive
                drive_service = GoogleDriveService(drive_integration)
                result = drive_service.upload_file(
                    temp_file_path,
                    folder_id=folder_id,
                    filename=uploaded_file.name
                )
                
                # Clean up temp file
                os.unlink(temp_file_path)
                
                return JsonResponse({
                    'success': True,
                    'file_id': result['id'],
                    'file_name': result['name'],
                    'web_view_link': result['webViewLink']
                })
                
            except Exception as e:
                # Clean up temp file on error
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                raise e
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def integration_logs(request, integration_id):
    """View integration logs."""
    integration = get_object_or_404(
        Integration,
        id=integration_id,
        created_by=request.user
    )
    
    logs = IntegrationLog.objects.filter(integration=integration)
    
    context = {
        'integration': integration,
        'logs': logs
    }
    
    return render(request, 'integrations/integration_logs.html', context)


@login_required
def test_integration(request, integration_id):
    """Test integration connection."""
    try:
        integration = get_object_or_404(
            Integration,
            id=integration_id,
            created_by=request.user
        )
        
        if integration.integration_type == 'google_drive':
            drive_integration = integration.google_drive
            drive_service = GoogleDriveService(drive_integration)
            
            if drive_service.test_connection():
                integration.status = 'connected'
                integration.last_sync = timezone.now()
                integration.save()
                
                messages.success(request, f'{integration.name} connection test successful!')
            else:
                integration.status = 'error'
                integration.save()
                
                messages.error(request, f'{integration.name} connection test failed!')
        else:
            messages.warning(request, f'Connection testing not implemented for {integration.integration_type}')
        
    except Exception as e:
        messages.error(request, f'Connection test failed: {str(e)}')
    
    return redirect('integrations:integration_hub')


@login_required
def delete_integration(request, integration_id):
    """Delete integration."""
    try:
        integration = get_object_or_404(
            Integration,
            id=integration_id,
            created_by=request.user
        )
        
        # Delete related objects
        if hasattr(integration, 'google_drive'):
            integration.google_drive.delete()
        
        integration.delete()
        messages.success(request, f'{integration.name} integration deleted successfully.')
        
    except Exception as e:
        messages.error(request, f'Failed to delete integration: {str(e)}')
    
    return redirect('integrations:integration_hub')
