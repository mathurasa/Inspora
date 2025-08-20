"""
Google Drive integration service for Inspora platform.
"""
import os
import json
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from io import BytesIO
import mimetypes


class GoogleDriveService:
    """
    Service for interacting with Google Drive API.
    """
    
    def __init__(self, integration):
        """
        Initialize the Google Drive service.
        
        Args:
            integration: GoogleDriveIntegration instance
        """
        self.integration = integration
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Drive API."""
        try:
            # Check if we have valid credentials
            if not self.integration.is_token_valid():
                if self.integration.needs_refresh():
                    self._refresh_token()
                else:
                    raise Exception("No valid credentials available")
            
            # Create credentials object
            creds = Credentials(
                token=self.integration.access_token,
                refresh_token=self.integration.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_OAUTH2_CLIENT_ID,
                client_secret=settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            
            # Build the service
            self.service = build('drive', 'v3', credentials=creds)
            
        except Exception as e:
            # Log the error
            self._log_error(f"Authentication failed: {str(e)}")
            raise
    
    def _refresh_token(self):
        """Refresh the access token."""
        try:
            creds = Credentials(
                token=None,
                refresh_token=self.integration.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_OAUTH2_CLIENT_ID,
                client_secret=settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            
            # Refresh the token
            creds.refresh(Request())
            
            # Update the integration
            self.integration.access_token = creds.token
            self.integration.token_expiry = timezone.now() + timedelta(seconds=creds.expiry.timestamp() - datetime.now().timestamp())
            self.integration.save()
            
        except Exception as e:
            self._log_error(f"Token refresh failed: {str(e)}")
            raise
    
    def _log_error(self, message, details=None):
        """Log an error to the integration log."""
        from .models import IntegrationLog
        
        IntegrationLog.objects.create(
            integration=self.integration.integration,
            level='error',
            message=message,
            details=details or {}
        )
    
    def list_files(self, folder_id=None, query=None, page_size=50):
        """
        List files from Google Drive.
        
        Args:
            folder_id: ID of the folder to list (None for root)
            query: Custom query string
            page_size: Number of items per page
            
        Returns:
            List of file metadata
        """
        try:
            if not self.service:
                raise Exception("Service not authenticated")
            
            # Build query
            if folder_id:
                q = f"'{folder_id}' in parents and trashed=false"
            else:
                q = "trashed=false"
            
            if query:
                q += f" and {query}"
            
            # Execute query
            results = self.service.files().list(
                q=q,
                pageSize=page_size,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, parents, webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            
            # Log success
            self._log_success(f"Listed {len(files)} files")
            
            return files
            
        except Exception as e:
            self._log_error(f"Failed to list files: {str(e)}")
            raise
    
    def get_file(self, file_id):
        """
        Get file metadata.
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            File metadata
        """
        try:
            if not self.service:
                raise Exception("Service not authenticated")
            
            file_metadata = self.service.files().get(
                id=file_id,
                fields="id, name, mimeType, size, modifiedTime, parents, webViewLink, description"
            ).execute()
            
            self._log_success(f"Retrieved file: {file_metadata.get('name')}")
            return file_metadata
            
        except Exception as e:
            self._log_error(f"Failed to get file {file_id}: {str(e)}")
            raise
    
    def download_file(self, file_id, destination_path=None):
        """
        Download a file from Google Drive.
        
        Args:
            file_id: Google Drive file ID
            destination_path: Local path to save file (optional)
            
        Returns:
            File content as bytes or saves to destination
        """
        try:
            if not self.service:
                raise Exception("Service not authenticated")
            
            # Get file metadata
            file_metadata = self.get_file(file_id)
            
            # Download file content
            request = self.service.files().get_media(id=file_id)
            file_content = BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            content = file_content.getvalue()
            
            # Save to destination if specified
            if destination_path:
                with open(destination_path, 'wb') as f:
                    f.write(content)
                self._log_success(f"Downloaded file to: {destination_path}")
            else:
                self._log_success(f"Downloaded file: {file_metadata.get('name')}")
            
            return content
            
        except Exception as e:
            self._log_error(f"Failed to download file {file_id}: {str(e)}")
            raise
    
    def upload_file(self, file_path, folder_id=None, filename=None):
        """
        Upload a file to Google Drive.
        
        Args:
            file_path: Local path to the file
            folder_id: ID of the folder to upload to (None for root)
            filename: Custom filename (optional)
            
        Returns:
            Uploaded file metadata
        """
        try:
            if not self.service:
                raise Exception("Service not authenticated")
            
            # Get file info
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if not filename:
                filename = os.path.basename(file_path)
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            # Prepare file metadata
            file_metadata = {
                'name': filename,
                'mimeType': mime_type
            }
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Upload file
            media = MediaIoBaseUpload(
                open(file_path, 'rb'),
                mimetype=mime_type,
                resumable=True
            )
            
            file_obj = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, mimeType, size, webViewLink'
            ).execute()
            
            self._log_success(f"Uploaded file: {file_obj.get('name')}")
            return file_obj
            
        except Exception as e:
            self._log_error(f"Failed to upload file {file_path}: {str(e)}")
            raise
    
    def create_folder(self, folder_name, parent_folder_id=None):
        """
        Create a new folder in Google Drive.
        
        Args:
            folder_name: Name of the folder to create
            parent_folder_id: ID of the parent folder (None for root)
            
        Returns:
            Created folder metadata
        """
        try:
            if not self.service:
                raise Exception("Service not authenticated")
            
            # Prepare folder metadata
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                folder_metadata['parents'] = [parent_folder_id]
            
            # Create folder
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id, name, mimeType, webViewLink'
            ).execute()
            
            self._log_success(f"Created folder: {folder.get('name')}")
            return folder
            
        except Exception as e:
            self._log_error(f"Failed to create folder {folder_name}: {str(e)}")
            raise
    
    def delete_file(self, file_id):
        """
        Delete a file from Google Drive.
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            True if successful
        """
        try:
            if not self.service:
                raise Exception("Service not authenticated")
            
            self.service.files().delete(id=file_id).execute()
            
            self._log_success(f"Deleted file: {file_id}")
            return True
            
        except Exception as e:
            self._log_error(f"Failed to delete file {file_id}: {str(e)}")
            raise
    
    def share_file(self, file_id, email, role='reader', notify=True):
        """
        Share a file with another user.
        
        Args:
            file_id: Google Drive file ID
            email: Email of the user to share with
            role: Permission role (reader, writer, owner)
            notify: Whether to send notification email
            
        Returns:
            Permission metadata
        """
        try:
            if not self.service:
                raise Exception("Service not authenticated")
            
            # Check if already shared
            permissions = self.service.permissions().list(fileId=file_id).execute()
            
            for permission in permissions.get('permissions', []):
                if permission.get('emailAddress') == email:
                    # Update existing permission
                    permission_obj = self.service.permissions().update(
                        fileId=file_id,
                        permissionId=permission['id'],
                        body={'role': role}
                    ).execute()
                    self._log_success(f"Updated sharing for {email} on file {file_id}")
                    return permission_obj
            
            # Create new permission
            permission = {
                'type': 'user',
                'role': role,
                'emailAddress': email
            }
            
            permission_obj = self.service.permissions().create(
                fileId=file_id,
                body=permission,
                sendNotificationEmail=notify
            ).execute()
            
            self._log_success(f"Shared file {file_id} with {email}")
            return permission_obj
            
        except Exception as e:
            self._log_error(f"Failed to share file {file_id} with {email}: {str(e)}")
            raise
    
    def _log_success(self, message, details=None):
        """Log a success message to the integration log."""
        from .models import IntegrationLog
        
        IntegrationLog.objects.create(
            integration=self.integration.integration,
            level='success',
            message=message,
            details=details or {}
        )
    
    def test_connection(self):
        """
        Test the connection to Google Drive.
        
        Returns:
            True if connection is successful
        """
        try:
            if not self.service:
                raise Exception("Service not authenticated")
            
            # Try to list files from root
            self.service.files().list(pageSize=1).execute()
            
            self._log_success("Connection test successful")
            return True
            
        except Exception as e:
            self._log_error(f"Connection test failed: {str(e)}")
            return False






