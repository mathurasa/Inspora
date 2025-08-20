# 🔐 Google OAuth2 Setup Guide for Inspora

## 🚨 **Current Issue: "OAuth client was not found" Error**

The error `Error 401: invalid_client` occurs because:
1. **Missing Google OAuth URLs** ✅ **FIXED**
2. **Placeholder OAuth credentials** ❌ **NEEDS YOUR ACTION**
3. **Redirect URI mismatch** ❌ **NEEDS YOUR ACTION**

## ✅ **What I've Fixed**

1. **Added missing Google OAuth URLs** to `accounts/urls.py`:
   - `/accounts/google/login/` → Google OAuth login
   - `/accounts/google/callback/` → Google OAuth callback

2. **Fixed login template** to use correct URL namespace

## 🔧 **What You Need to Do**

### **Step 1: Create Google OAuth2 Credentials**

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create a new project** or select existing one
3. **Enable Google+ API**:
   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API" and enable it
4. **Create OAuth2 Credentials**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Web application"

### **Step 2: Configure OAuth2 Client**

**Application Type**: Web application
**Name**: Inspora (or your preferred name)
**Authorized JavaScript origins**:
```
http://localhost:8000
http://127.0.0.1:8000
```

**Authorized redirect URIs**:
```
http://localhost:8000/accounts/google/callback/
http://127.0.0.1:8000/accounts/google/callback/
```

### **Step 3: Update Your .env File**

Replace the placeholder values in your `.env` file:

```bash
# Current (placeholder values - NOT WORKING)
GOOGLE_OAUTH2_CLIENT_ID=placeholder-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=placeholder-client-secret
GOOGLE_OAUTH2_REDIRECT_URI=http://localhost:8000/google/callback/

# New (your actual Google OAuth credentials)
GOOGLE_OAUTH2_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
GOOGLE_OAUTH2_CLIENT_SECRET=your-actual-client-secret
GOOGLE_OAUTH2_REDIRECT_URI=http://localhost:8000/accounts/google/callback/
```

### **Step 4: Restart Django Server**

After updating the `.env` file:

```bash
# Stop the current server (Ctrl+C)
# Then restart
source venv/bin/activate
python manage.py runserver
```

## 🧪 **Testing the Fix**

1. **Visit**: `http://localhost:8000/login/`
2. **Click**: "Google" button
3. **Expected**: Redirect to Google OAuth consent screen
4. **After consent**: Redirect back to your app and create/login user

## 🔍 **Troubleshooting**

### **Common Issues & Solutions**

#### **Issue 1: "OAuth client was not found"**
- **Cause**: Invalid client ID or client secret
- **Solution**: Double-check credentials in `.env` file

#### **Issue 2: "Redirect URI mismatch"**
- **Cause**: Redirect URI in Google Console doesn't match your app
- **Solution**: Ensure exact match: `http://localhost:8000/accounts/google/callback/`

#### **Issue 3: "Google+ API not enabled"**
- **Cause**: API not enabled in Google Cloud Console
- **Solution**: Enable Google+ API in your project

#### **Issue 4: "Invalid scope"**
- **Cause**: OAuth scopes not properly configured
- **Solution**: Current scopes are correct: `openid email profile`

### **Debug Steps**

1. **Check Django logs**:
   ```bash
   tail -f logs/django.log
   ```

2. **Verify environment variables**:
   ```python
   # In Django shell
   python manage.py shell
   >>> from django.conf import settings
   >>> print(settings.GOOGLE_OAUTH2_CLIENT_ID)
   >>> print(settings.GOOGLE_OAUTH2_CLIENT_SECRET)
   >>> print(settings.GOOGLE_OAUTH2_REDIRECT_URI)
   ```

3. **Test OAuth URL generation**:
   ```python
   # In Django shell
   >>> from accounts.google_auth import get_google_oauth2_url
   >>> print(get_google_oauth2_url())
   ```

## 📱 **Production Considerations**

When deploying to production:

1. **Update redirect URIs** in Google Console
2. **Use environment variables** for credentials
3. **Enable HTTPS** (Google OAuth requires secure connections)
4. **Set proper domain** in authorized origins

## 🎯 **Expected Flow After Fix**

1. **User clicks "Google"** on login page
2. **Redirect to Google** OAuth consent screen
3. **User consents** to permissions
4. **Google redirects back** to `/accounts/google/callback/`
5. **Django processes** the OAuth callback
6. **User is authenticated** and redirected to dashboard
7. **New users are created** automatically with Google info

## 🆘 **Still Having Issues?**

If you continue to experience problems:

1. **Check Django logs** for detailed error messages
2. **Verify all environment variables** are set correctly
3. **Ensure Google Cloud Console** settings match exactly
4. **Test with a simple OAuth flow** first

---

**Remember**: Never commit real OAuth credentials to version control. Always use environment variables or secure configuration management.





