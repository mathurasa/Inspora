"""
Google OAuth2 authentication backend for Django.
"""
import json
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import ValidationError
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

User = get_user_model()


class GoogleOAuth2Backend(BaseBackend):
    """
    Custom authentication backend for Google OAuth2.
    """
    
    def authenticate(self, request, google_id_token=None, **kwargs):
        """
        Authenticate a user using Google ID token.
        """
        if not google_id_token:
            return None
            
        try:
            # Check if Google OAuth2 is properly configured
            if not settings.GOOGLE_OAUTH2_CLIENT_ID:
                print("Google OAuth2 not configured: Missing CLIENT_ID")
                return None
                
            # Verify the Google ID token
            idinfo = id_token.verify_oauth2_token(
                google_id_token, 
                google_requests.Request(), 
                settings.GOOGLE_OAUTH2_CLIENT_ID
            )
            
            # Extract user information
            google_user_id = idinfo['sub']
            email = idinfo['email']
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')
            picture = idinfo.get('picture', '')
            
            # Try to find existing user by email
            try:
                user = User.objects.get(email=email)
                # Update user information if needed
                if not user.first_name and first_name:
                    user.first_name = first_name
                if not user.last_name and last_name:
                    user.last_name = last_name
                user.save()
                return user
            except User.DoesNotExist:
                # Create new user
                username = self._generate_unique_username(email)
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=None  # No password for OAuth users
                )
                user.is_verified = True  # Google users are verified
                user.save()
                return user
                
        except Exception as e:
            # Log the error for debugging
            print(f"Google OAuth2 authentication error: {e}")
            return None
    
    def get_user(self, user_id):
        """
        Get user by ID.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
    
    def _generate_unique_username(self, email):
        """
        Generate a unique username from email.
        """
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
            
        return username


def get_google_oauth2_url():
    """
    Generate Google OAuth2 authorization URL.
    """
    client_id = settings.GOOGLE_OAUTH2_CLIENT_ID
    redirect_uri = settings.GOOGLE_OAUTH2_REDIRECT_URI
    
    # Check if Google OAuth2 is properly configured
    if not client_id:
        raise ValidationError("Google OAuth2 not configured: Missing CLIENT_ID")
    
    scope = 'openid email profile'
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope}&"
        f"response_type=code&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    return auth_url


def exchange_code_for_token(authorization_code):
    """
    Exchange authorization code for access token.
    """
    client_id = settings.GOOGLE_OAUTH2_CLIENT_ID
    client_secret = settings.GOOGLE_OAUTH2_CLIENT_SECRET
    redirect_uri = settings.GOOGLE_OAUTH2_REDIRECT_URI
    
    # Check if Google OAuth2 is properly configured
    if not client_id or not client_secret:
        raise ValidationError("Google OAuth2 not configured: Missing CLIENT_ID or CLIENT_SECRET")
    
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': authorization_code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
    }
    
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise ValidationError(f"Failed to exchange code for token: {response.text}")


def get_user_info_from_token(access_token):
    """
    Get user information from Google using access token.
    """
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.get(userinfo_url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise ValidationError(f"Failed to get user info: {response.text}")
