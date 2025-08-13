"""
Management command to check Google OAuth2 configuration.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.urls import reverse


class Command(BaseCommand):
    help = 'Check Google OAuth2 configuration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Checking Google OAuth2 configuration...'))
        
        # Check required settings
        client_id = getattr(settings, 'GOOGLE_OAUTH2_CLIENT_ID', None)
        client_secret = getattr(settings, 'GOOGLE_OAUTH2_CLIENT_SECRET', None)
        redirect_uri = getattr(settings, 'GOOGLE_OAUTH2_REDIRECT_URI', None)
        
        # Display configuration status
        self.stdout.write(f'Client ID: {"✓ Set" if client_id else "✗ Missing"}')
        self.stdout.write(f'Client Secret: {"✓ Set" if client_secret else "✗ Missing"}')
        self.stdout.write(f'Redirect URI: {"✓ Set" if redirect_uri else "✗ Missing"}')
        
        if not client_id or not client_secret:
            self.stdout.write(self.style.ERROR('\nGoogle OAuth2 is not properly configured!'))
            self.stdout.write(self.style.WARNING('\nTo fix this:'))
            self.stdout.write('1. Go to Google Cloud Console (https://console.cloud.google.com/)')
            self.stdout.write('2. Create a new project or select existing one')
            self.stdout.write('3. Enable Google+ API and Google OAuth2 API')
            self.stdout.write('4. Create OAuth2 credentials')
            self.stdout.write('5. Add the following to your .env file:')
            self.stdout.write('   GOOGLE_OAUTH2_CLIENT_ID=your_client_id_here')
            self.stdout.write('   GOOGLE_OAUTH2_CLIENT_SECRET=your_client_secret_here')
            self.stdout.write('   GOOGLE_OAUTH2_REDIRECT_URI=http://localhost:8000/google/callback/')
        else:
            self.stdout.write(self.style.SUCCESS('\nGoogle OAuth2 is properly configured!'))
            
        # Check URL configuration
        try:
            login_url = reverse('google_login')
            callback_url = reverse('google_callback')
            self.stdout.write(f'\nURLs:')
            self.stdout.write(f'Login: {login_url}')
            self.stdout.write(f'Callback: {callback_url}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nURL configuration error: {e}'))
