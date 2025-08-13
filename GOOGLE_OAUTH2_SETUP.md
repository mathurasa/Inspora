# Google OAuth2 Setup Guide for Inspora

This guide will help you set up Google OAuth2 authentication for the Inspora platform.

## Prerequisites

- A Google account
- Access to Google Cloud Console
- Inspora project running locally

## Step-by-Step Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" at the top
3. Click "New Project"
4. Enter a project name (e.g., "Inspora OAuth2")
5. Click "Create"

### 2. Enable Required APIs

1. In your project, go to "APIs & Services" > "Library"
2. Search for and enable these APIs:
   - **Google+ API** (for user profile information)
   - **Google OAuth2 API** (for authentication)

### 3. Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. If prompted, configure the OAuth consent screen:
   - User Type: External
   - App name: Inspora
   - User support email: your-email@gmail.com
   - Developer contact information: your-email@gmail.com
4. Click "Save and Continue" through the remaining steps
5. Back to credentials, click "Create Credentials" > "OAuth 2.0 Client IDs"
6. Application type: **Web application**
7. Name: Inspora OAuth2
8. Authorized redirect URIs: `http://localhost:8000/google/callback/`
9. Click "Create"

### 4. Copy Credentials

After creating the credentials, you'll see:
- **Client ID** (copy this)
- **Client Secret** (copy this)

### 5. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` and add your Google OAuth2 credentials:
   ```bash
   # Google OAuth2 Configuration
   GOOGLE_OAUTH2_CLIENT_ID=your-actual-client-id-here
   GOOGLE_OAUTH2_CLIENT_SECRET=your-actual-client-secret-here
   GOOGLE_OAUTH2_REDIRECT_URI=http://localhost:8000/google/callback/
   ```

### 6. Test Configuration

Run the configuration check command:
```bash
python3 manage.py check_google_oauth2
```

You should see:
```
Checking Google OAuth2 configuration...
Client ID: ✓ Set
Client Secret: ✓ Set
Redirect URI: ✓ Set

Google OAuth2 is properly configured!

URLs:
Login: /google/login/
Callback: /google/callback/
```

### 7. Test Google Sign-In

1. Start your Django server:
   ```bash
   python3 manage.py runserver
   ```

2. Go to `http://localhost:8000/login/`
3. Click the "Google" button
4. You should be redirected to Google's OAuth consent screen
5. After authorization, you'll be redirected back to Inspora

## Troubleshooting

### Common Issues

#### 1. "Google OAuth2 not configured" Error
- Check that your `.env` file has the correct credentials
- Ensure the environment variables are loaded
- Restart your Django server after updating `.env`

#### 2. "Invalid redirect URI" Error
- Verify the redirect URI in Google Cloud Console matches exactly: `http://localhost:8000/google/callback/`
- Check for trailing slashes or typos

#### 3. "Client ID not found" Error
- Ensure the Client ID is copied correctly from Google Cloud Console
- Check that the `.env` file is in the project root directory

#### 4. 404 Error on Google Login
- Verify the URL configuration in `inspora/urls.py`
- Check that the server is running and accessible

### Debug Commands

Check Google OAuth2 configuration:
```bash
python3 manage.py check_google_oauth2
```

Check Django URLs:
```bash
python3 manage.py show_urls | grep google
```

Check environment variables:
```bash
python3 manage.py shell -c "from django.conf import settings; print('Client ID:', settings.GOOGLE_OAUTH2_CLIENT_ID)"
```

## Security Notes

- Never commit your `.env` file to version control
- Keep your Client Secret secure
- Use HTTPS in production
- Regularly rotate your OAuth2 credentials
- Monitor OAuth2 usage in Google Cloud Console

## Production Deployment

For production deployment:

1. Update the redirect URI to your production domain:
   ```
   GOOGLE_OAUTH2_REDIRECT_URI=https://yourdomain.com/google/callback/
   ```

2. Add your production domain to Google Cloud Console authorized redirect URIs

3. Consider using environment-specific configuration files

4. Enable HTTPS and secure cookies

## Support

If you encounter issues:

1. Check the Django server logs for error messages
2. Verify your Google Cloud Console configuration
3. Test with the configuration check command
4. Check the troubleshooting section above

For additional help, refer to:
- [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Django Authentication Documentation](https://docs.djangoproject.com/en/stable/topics/auth/)
- [Inspora Project Documentation](README.md)
