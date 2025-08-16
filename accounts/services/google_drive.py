"""
Google Drive service for document management.
"""
import os
import io
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from django.conf import settings
from django.utils import timezone
from ..models import GoogleDriveIntegration, Document, DocumentVersion


class GoogleDriveService:
    """
    Service class for Google Drive operations.
    """
    
    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.metadata.readonly'
    ]
    
    def __init__(self, user):
        self.user = user
        self.integration = None
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Drive API."""
        try:
            self.integration = GoogleDriveIntegration.objects.get(user=self.user, is_active=True)
            
            # Check if token is expired
            if self.integration.is_token_expired():
                self._refresh_token()
            
            # Build service
            credentials = Credentials(
                token=self.integration.access_token,
                refresh_token=self.integration.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_OAUTH2_CLIENT_ID,
                client_secret=settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                scopes=self.SCOPES
            )
            
            self.service = build('drive', 'v3', credentials=credentials)
            
        except GoogleDriveIntegration.DoesNotExist:
            raise Exception("Google Drive integration not found for this user")
    
    def _refresh_token(self):
        """Refresh the access token."""
        credentials = Credentials(
            token=self.integration.access_token,
            refresh_token=self.integration.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_OAUTH2_CLIENT_ID,
            client_secret=settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            scopes=self.SCOPES
        )
        
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            
            # Update integration
            self.integration.access_token = credentials.token
            self.integration.token_expiry = credentials.expiry
            self.integration.save()
    
    def list_files(self, folder_id=None, page_size=50):
        """List files from Google Drive."""
        try:
            query = "trashed=false"
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            results = self.service.files().list(
                pageSize=page_size,
                fields="nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime, parents, webViewLink, webContentLink)",
                q=query
            ).execute()
            
            return results.get('files', [])
            
        except Exception as e:
            print(f"Error listing Google Drive files: {e}")
            return []
    
    def get_file(self, file_id):
        """Get file metadata from Google Drive."""
        try:
            file_metadata = self.service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, size, createdTime, modifiedTime, parents, webViewLink, webContentLink"
            ).execute()
            
            return file_metadata
            
        except Exception as e:
            print(f"Error getting Google Drive file: {e}")
            return None
    
    def download_file(self, file_id, save_path=None):
        """Download a file from Google Drive."""
        try:
            file_metadata = self.get_file(file_id)
            if not file_metadata:
                return None
            
            # Download file content
            request = self.service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            file_content.seek(0)
            
            # Save to local path if specified
            if save_path:
                with open(save_path, 'wb') as f:
                    f.write(file_content.read())
                return save_path
            
            return file_content
            
        except Exception as e:
            print(f"Error downloading Google Drive file: {e}")
            return None
    
    def upload_file(self, file_path, folder_id=None, file_name=None):
        """Upload a file to Google Drive."""
        try:
            if not file_name:
                file_name = os.path.basename(file_path)
            
            file_metadata = {
                'name': file_name
            }
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Upload file
            media = MediaIoBaseUpload(
                io.BytesIO(open(file_path, 'rb').read()),
                mimetype='application/octet-stream',
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            
            return file
            
        except Exception as e:
            print(f"Error uploading file to Google Drive: {e}")
            return None
    
    def create_folder(self, folder_name, parent_folder_id=None):
        """Create a folder in Google Drive."""
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id, name'
            ).execute()
            
            return folder
            
        except Exception as e:
            print(f"Error creating Google Drive folder: {e}")
            return None
    
    def sync_documents(self):
        """Sync documents from Google Drive to local database."""
        try:
            files = self.list_files(page_size=100)
            
            for file_data in files:
                # Skip folders
                if file_data['mimeType'] == 'application/vnd.google-apps.folder':
                    continue
                
                # Check if document already exists
                document, created = Document.objects.get_or_create(
                    source_id=file_data['id'],
                    source='google_drive',
                    defaults={
                        'user': self.user,
                        'title': file_data['name'],
                        'file_name': file_data['name'],
                        'file_size': int(file_data.get('size', 0)),
                        'mime_type': file_data['mimeType'],
                        'source_url': file_data.get('webViewLink', ''),
                        'file_type': self._get_file_type(file_data['mimeType']),
                        'tags': ['google-drive', 'synced'],
                        'folder': self._get_folder_path(file_data.get('parents', []))
                    }
                )
                
                if not created:
                    # Update existing document
                    document.title = file_data['name']
                    document.file_size = int(file_data.get('size', 0))
                    document.mime_type = file_data['mimeType']
                    document.source_url = file_data.get('webViewLink', '')
                    document.updated_at = timezone.now()
                    document.save()
            
            # Update last sync time
            self.integration.last_sync = timezone.now()
            self.integration.save()
            
            return True
            
        except Exception as e:
            print(f"Error syncing Google Drive documents: {e}")
            return False
    
    def _get_file_type(self, mime_type):
        """Determine file type from MIME type."""
        if 'document' in mime_type:
            return 'document'
        elif 'spreadsheet' in mime_type:
            return 'spreadsheet'
        elif 'presentation' in mime_type:
            return 'presentation'
        elif 'image' in mime_type:
            return 'image'
        elif 'video' in mime_type:
            return 'video'
        elif 'audio' in mime_type:
            return 'audio'
        elif 'archive' in mime_type or 'zip' in mime_type:
            return 'archive'
        else:
            return 'other'
    
    def _get_folder_path(self, parent_ids):
        """Get folder path from parent IDs."""
        if not parent_ids:
            return 'root'
        
        try:
            parent = self.service.files().get(
                fileId=parent_ids[0],
                fields='name, parents'
            ).execute()
            
            if parent.get('parents'):
                return f"{self._get_folder_path(parent['parents'])}/{parent['name']}"
            else:
                return parent['name']
                
        except Exception:
            return 'unknown'


