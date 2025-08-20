"""
GitHub service for repository and file management.
"""
import os
import base64
import requests
from django.conf import settings
from django.utils import timezone
from ..models import GitHubIntegration, Document, DocumentVersion


class GitHubService:
    """
    Service class for GitHub operations.
    """
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, user):
        self.user = user
        self.integration = None
        self.headers = {}
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with GitHub API."""
        try:
            self.integration = GitHubIntegration.objects.get(user=self.user, is_active=True)
            self.headers = {
                'Authorization': f"{self.integration.token_type} {self.integration.access_token}",
                'Accept': 'application/vnd.github.v3+json'
            }
            
        except GitHubIntegration.DoesNotExist:
            raise Exception("GitHub integration not found for this user")
    
    def get_user_info(self):
        """Get authenticated user information."""
        try:
            response = requests.get(f"{self.BASE_URL}/user", headers=self.headers)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"Error getting GitHub user info: {e}")
            return None
    
    def list_repositories(self, visibility='all', sort='updated'):
        """List user repositories."""
        try:
            params = {
                'visibility': visibility,
                'sort': sort,
                'per_page': 100
            }
            
            response = requests.get(f"{self.BASE_URL}/user/repos", headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"Error listing GitHub repositories: {e}")
            return []
    
    def get_repository(self, repo_name):
        """Get repository information."""
        try:
            response = requests.get(f"{self.BASE_URL}/repos/{self.integration.github_username}/{repo_name}", headers=self.headers)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"Error getting GitHub repository: {e}")
            return None
    
    def list_files(self, repo_name, path='', branch='main'):
        """List files in a repository."""
        try:
            url = f"{self.BASE_URL}/repos/{self.integration.github_username}/{repo_name}/contents/{path}"
            params = {'ref': branch}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            contents = response.json()
            if isinstance(contents, dict):
                contents = [contents]
            
            return contents
            
        except Exception as e:
            print(f"Error listing GitHub files: {e}")
            return []
    
    def get_file_content(self, repo_name, file_path, branch='main'):
        """Get file content from GitHub."""
        try:
            url = f"{self.BASE_URL}/repos/{self.integration.github_username}/{repo_name}/contents/{file_path}"
            params = {'ref': branch}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            file_data = response.json()
            
            # Decode content if it's base64 encoded
            if file_data.get('encoding') == 'base64':
                content = base64.b64decode(file_data['content']).decode('utf-8')
                file_data['decoded_content'] = content
            
            return file_data
            
        except Exception as e:
            print(f"Error getting GitHub file content: {e}")
            return None
    
    def download_file(self, repo_name, file_path, save_path=None, branch='main'):
        """Download a file from GitHub."""
        try:
            file_data = self.get_file_content(repo_name, file_path, branch)
            if not file_data:
                return None
            
            # Get raw content
            raw_url = file_data['download_url']
            response = requests.get(raw_url, headers=self.headers)
            response.raise_for_status()
            
            content = response.content
            
            # Save to local path if specified
            if save_path:
                with open(save_path, 'wb') as f:
                    f.write(content)
                return save_path
            
            return content
            
        except Exception as e:
            print(f"Error downloading GitHub file: {e}")
            return None
    
    def upload_file(self, repo_name, file_path, content, message="Upload file", branch='main'):
        """Upload a file to GitHub."""
        try:
            url = f"{self.BASE_URL}/repos/{self.integration.github_username}/{repo_name}/contents/{file_path}"
            
            # Check if file exists
            existing_file = self.get_file_content(repo_name, file_path, branch)
            
            data = {
                'message': message,
                'content': base64.b64encode(content.encode('utf-8')).decode('utf-8'),
                'branch': branch
            }
            
            if existing_file:
                data['sha'] = existing_file['sha']
            
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error uploading file to GitHub: {e}")
            return None
    
    def create_repository(self, name, description="", private=False, auto_init=True):
        """Create a new repository."""
        try:
            data = {
                'name': name,
                'description': description,
                'private': private,
                'auto_init': auto_init
            }
            
            response = requests.post(f"{self.BASE_URL}/user/repos", headers=self.headers, json=data)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error creating GitHub repository: {e}")
            return None
    
    def sync_documents(self, repo_name=None):
        """Sync documents from GitHub to local database."""
        try:
            if repo_name:
                repos = [self.get_repository(repo_name)]
            else:
                repos = self.list_repositories()
            
            for repo in repos:
                if not repo:
                    continue
                
                # Get files from repository
                files = self.list_files(repo['name'])
                
                for file_data in files:
                    # Skip directories
                    if file_data['type'] == 'dir':
                        continue
                    
                    # Check if document already exists
                    document, created = Document.objects.get_or_create(
                        source_id=file_data['sha'],
                        source='github',
                        defaults={
                            'user': self.user,
                            'title': file_data['name'],
                            'file_name': file_data['name'],
                            'file_size': int(file_data.get('size', 0)),
                            'mime_type': self._get_mime_type(file_data['name']),
                            'source_url': file_data['html_url'],
                            'file_type': self._get_file_type(file_data['name']),
                            'tags': ['github', 'synced', repo['name']],
                            'folder': f"{repo['name']}/{os.path.dirname(file_data['path'])}" if os.path.dirname(file_data['path']) else repo['name']
                        }
                    )
                    
                    if not created:
                        # Update existing document
                        document.title = file_data['name']
                        document.file_size = int(file_data.get('size', 0))
                        document.source_url = file_data['html_url']
                        document.updated_at = timezone.now()
                        document.save()
            
            # Update last sync time
            self.integration.last_sync = timezone.now()
            self.integration.save()
            
            return True
            
        except Exception as e:
            print(f"Error syncing GitHub documents: {e}")
            return False
    
    def _get_mime_type(self, filename):
        """Get MIME type based on file extension."""
        ext = os.path.splitext(filename)[1].lower()
        
        mime_types = {
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.py': 'text/x-python',
            '.js': 'application/javascript',
            '.html': 'text/html',
            '.css': 'text/css',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.zip': 'application/zip',
            '.rar': 'application/x-rar-compressed',
            '.tar': 'application/x-tar',
            '.gz': 'application/gzip'
        }
        
        return mime_types.get(ext, 'application/octet-stream')
    
    def _get_file_type(self, filename):
        """Determine file type from filename."""
        ext = os.path.splitext(filename)[1].lower()
        
        if ext in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml']:
            return 'document'
        elif ext in ['.xls', '.xlsx', '.csv']:
            return 'spreadsheet'
        elif ext in ['.ppt', '.pptx']:
            return 'presentation'
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg']:
            return 'image'
        elif ext in ['.mp4', '.avi', '.mov']:
            return 'video'
        elif ext in ['.mp3', '.wav', '.flac']:
            return 'audio'
        elif ext in ['.zip', '.rar', '.tar', '.gz']:
            return 'archive'
        else:
            return 'other'






