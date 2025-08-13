# Google OAuth2 Setup Guide for Inspora

This guide will help you set up Google OAuth2 authentication for the Inspora platform.

## Prerequisites

- Google Cloud Console account
- Django project with the accounts app configured
- Google OAuth2 dependencies installed

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API and Google OAuth2 API

## Step 2: Configure OAuth2 Credentials

1. In the Google Cloud Console, go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth 2.0 Client IDs**
3. Choose **Web application** as the application type
4. Set the following:
   - **Name**: Inspora OAuth2 Client
   - **Authorized JavaScript origins**:
     - `http://localhost:8000`
     - `http://127.0.0.1:8000`
     - `http://192.168.8.138:8000` (your local network IP)
   - **Authorized redirect URIs**:
     - `http://localhost:8000/accounts/google/callback/`
     - `http://127.0.0.1:8000/accounts/google/callback/`
     - `http://192.168.8.138:8000/accounts/google/callback/`

5. Click **Create**
6. Note down your **Client ID** and **Client Secret**

## Step 3: Configure Environment Variables

1. Copy your `.env.example` file to `.env`:
   ```bash
   cp env.example .env
   ```

2. Update the `.env` file with your Google OAuth2 credentials:
   ```bash
   # Google OAuth2 Configuration
   GOOGLE_OAUTH2_CLIENT_ID=your-actual-client-id
   GOOGLE_OAUTH2_CLIENT_SECRET=your-actual-client-secret
   GOOGLE_OAUTH2_REDIRECT_URI=http://localhost:8000/accounts/google/callback/
   ```

## Step 4: Test the Integration

1. Start your Django server:
   ```bash
   export ALLOWED_HOSTS="localhost,127.0.0.1,0.0.0.0,192.168.8.138"
   source venv/bin/activate
   python manage.py runserver 0.0.0.0:8000
   ```

2. Visit the registration or login page
3. Click the **Google** button
4. You should be redirected to Google's OAuth consent screen
5. After authorization, you'll be redirected back to Inspora

## Features

### What's Included

✅ **Google Sign-In Button**: On both registration and login pages  
✅ **OAuth2 Flow**: Complete Google OAuth2 authentication flow  
✅ **User Creation**: Automatically creates new users from Google accounts  
✅ **Profile Sync**: Syncs Google profile information (name, email)  
✅ **Account Linking**: Links existing accounts by email address  
✅ **Secure Authentication**: Uses Google's secure ID tokens  

### User Experience

- **New Users**: Can sign up directly with Google
- **Existing Users**: Can link their Google account to existing Inspora account
- **Profile Information**: Automatically populated from Google profile
- **Verification**: Google users are automatically verified

## Security Considerations

1. **Client Secret**: Never expose your client secret in client-side code
2. **HTTPS**: Use HTTPS in production for secure OAuth2 flow
3. **Token Validation**: All Google ID tokens are validated server-side
4. **Scope Limitation**: Only requests necessary scopes (openid, email, profile)

## Troubleshooting

### Common Issues

1. **"Invalid Client ID" Error**
   - Check that your client ID is correct in the `.env` file
   - Verify the client ID in Google Cloud Console

2. **"Redirect URI Mismatch" Error**
   - Ensure your redirect URI exactly matches what's configured in Google Cloud Console
   - Check for trailing slashes and protocol (http vs https)

3. **"Invalid Scope" Error**
   - Verify that the Google+ API is enabled in your Google Cloud project

4. **"Access Denied" Error**
   - Check that your OAuth consent screen is properly configured
   - Ensure the app is not in testing mode if you want public access

### Debug Mode

To enable debug logging for OAuth2, add this to your Django settings:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'accounts.google_auth': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Production Deployment

When deploying to production:

1. **Update Redirect URIs**: Add your production domain to authorized redirect URIs
2. **Use HTTPS**: OAuth2 requires HTTPS in production
3. **Environment Variables**: Set production OAuth2 credentials securely
4. **Domain Verification**: Verify your domain with Google if needed

## Support

If you encounter issues:

1. Check the Django logs for detailed error messages
2. Verify your Google Cloud Console configuration
3. Ensure all environment variables are set correctly
4. Test with a fresh browser session (clear cookies/cache)

## Next Steps

After setting up Google OAuth2, you can:

1. **Add More Providers**: Implement Microsoft, GitHub, or other OAuth2 providers
2. **Enhanced Profile Sync**: Sync additional profile fields from Google
3. **Team Integration**: Automatically add users to teams based on Google Workspace
4. **Analytics**: Track OAuth2 usage and user engagement
