# OAuth Setup Guide - Production Ready

## 🎯 Quick Start

Your Langflow now supports **Google OAuth** and **Phantom Wallet** authentication!

### ✅ What's Been Implemented

1. **Backend OAuth Endpoints** (`/api/v1/oauth/`)
   - Google OAuth flow with CSRF protection
   - Phantom wallet Web3 authentication
   - Automatic user creation on first login
   - JWT token generation

2. **Frontend OAuth Buttons**
   - Google sign-in button with Google branding
   - Phantom wallet button with Phantom branding
   - Loading states and error handling
   - Responsive design

3. **Database Changes**
   - Added `oauth_provider` field (google, phantom)
   - Added `oauth_id` field (provider-specific user ID)
   - Added `wallet_address` field (for Web3)
   - Indexed for fast lookups

4. **Multi-Tenant Support**
   - Each OAuth user gets their own isolated data
   - Automatic folder creation
   - Per-user flows, variables, and API keys

---

## 🔐 Google OAuth Setup

### Step 1: Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google+ API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API"
   - Click "Enable"

4. Create OAuth 2.0 Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: **Web application**
   - Name: `Langflow OAuth`
   
5. Add Authorized Redirect URIs:
   ```
   Development:
   http://localhost:7860/api/v1/oauth/google/callback
   
   Production:
   https://yourdomain.com/api/v1/oauth/google/callback
   ```

6. Copy your **Client ID** and **Client Secret**

### Step 2: Configure Langflow

Edit your `.env` file:

```bash
# Google OAuth Credentials
LANGFLOW_GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
LANGFLOW_GOOGLE_CLIENT_SECRET=your-client-secret-here
```

### Step 3: Restart Langflow

```powershell
# Stop current server
Stop-Process -Name python,langflow -Force -ErrorAction SilentlyContinue

# Start with new configuration
$env:LANGFLOW_AUTO_LOGIN='false'
$env:LANGFLOW_NEW_USER_IS_ACTIVE='true'
$env:LANGFLOW_GOOGLE_CLIENT_ID='your-client-id'
$env:LANGFLOW_GOOGLE_CLIENT_SECRET='your-client-secret'
$env:Path = "C:\Users\new\.local\bin;$env:Path"
cd e:\langflow\langflow
uv run langflow run --host 127.0.0.1 --port 7860
```

### Step 4: Test Google Sign-In

1. Open http://localhost:7860/login
2. Click "Sign in with Google"
3. Authorize the app
4. You'll be redirected back and automatically logged in!

---

## 👻 Phantom Wallet Setup

### No Configuration Required!

Phantom wallet authentication works out of the box:

1. Users need to install [Phantom Browser Extension](https://phantom.app/)
2. Click "Sign in with Phantom" on login/signup page
3. Approve the connection in Phantom
4. Sign the authentication message
5. Automatically logged in!

### How It Works

1. Frontend requests a message from `/api/v1/oauth/phantom/message`
2. User signs the message with their Phantom wallet
3. Signature is sent to `/api/v1/oauth/phantom/verify`
4. Backend creates/finds user by wallet address
5. JWT tokens are issued

---

## 🚀 Production Deployment Checklist

### Security

- [ ] **SSL/TLS Required**: Use HTTPS in production
  ```bash
  LANGFLOW_REFRESH_SECURE=true
  LANGFLOW_ACCESS_SECURE=true
  ```

- [ ] **Update Redirect URIs**: Add production domain to Google Console
- [ ] **Strong Secrets**: Use long, random strings for JWT secrets
- [ ] **Rate Limiting**: Implement rate limiting on OAuth endpoints
- [ ] **CORS Configuration**: Restrict CORS to your domain
  ```bash
  LANGFLOW_CORS_ORIGINS=https://yourdomain.com
  ```

### Database

- [ ] **Connection Pooling**: Already configured (10 connections, 20 max)
- [ ] **SSL Mode**: Enable SSL for PostgreSQL
  ```bash
  LANGFLOW_DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require"
  ```

### Monitoring

- [ ] **Enable Logging**:
  ```bash
  LANGFLOW_LOG_LEVEL=info
  LANGFLOW_LOG_FILE=logs/langflow.log
  ```

- [ ] **Monitor OAuth Endpoints**: Track success/failure rates
- [ ] **Database Connection Health**: Monitor pool usage

### Environment Variables (Production)

```bash
# Core
LANGFLOW_AUTO_LOGIN=false
LANGFLOW_NEW_USER_IS_ACTIVE=true
LANGFLOW_SUPERUSER=admin
LANGFLOW_SUPERUSER_PASSWORD=<strong-password>

# Database
LANGFLOW_DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
LANGFLOW_POOL_SIZE=20
LANGFLOW_MAX_OVERFLOW=40

# Security
LANGFLOW_REFRESH_SECURE=true
LANGFLOW_ACCESS_SECURE=true
LANGFLOW_REFRESH_SAME_SITE=strict
LANGFLOW_CORS_ORIGINS=https://yourdomain.com

# Google OAuth
LANGFLOW_GOOGLE_CLIENT_ID=<your-client-id>
LANGFLOW_GOOGLE_CLIENT_SECRET=<your-client-secret>

# Monitoring
LANGFLOW_LOG_LEVEL=info
LANGFLOW_LOG_FILE=/var/log/langflow/langflow.log
```

---

## 📊 User Experience

### Login Page
- Traditional username/password
- "Or continue with" divider
- Google button with icon
- Phantom button with icon
- Link to signup page

### Signup Page
- Traditional registration form
- "Or continue with" divider
- Google button (creates account automatically)
- Phantom button (creates account automatically)
- Link to login page

### First-Time OAuth Users
1. Click OAuth button
2. Authorize the provider
3. Account automatically created
4. Default folder created
5. Redirected to dashboard

### Returning OAuth Users
1. Click OAuth button
2. Authorize the provider
3. Immediately logged in
4. No password needed!

---

## 🔍 Testing

### Test Google OAuth Flow

```bash
# 1. Start server with Google OAuth enabled
# 2. Open http://localhost:7860/login
# 3. Click "Sign in with Google"
# 4. Should redirect to Google consent screen
# 5. Authorize and return to app
# 6. Check PostgreSQL for new user:

psql $LANGFLOW_DATABASE_URL
SELECT username, oauth_provider, oauth_id FROM "user" WHERE oauth_provider='google';
```

### Test Phantom OAuth Flow

```bash
# 1. Install Phantom browser extension
# 2. Create/import a wallet
# 3. Open http://localhost:7860/login
# 4. Click "Sign in with Phantom"
# 5. Approve connection
# 6. Sign message
# 7. Check database:

psql $LANGFLOW_DATABASE_URL
SELECT username, oauth_provider, wallet_address FROM "user" WHERE oauth_provider='phantom';
```

### Test Multi-Tenant Isolation

```bash
# 1. Login as Google user, create a flow
# 2. Logout
# 3. Login as Phantom user, check flows
# 4. Should see NO flows from Google user
# 5. Create new flow as Phantom user
# 6. Logout and login as Google user again
# 7. Should NOT see Phantom user's flow
```

---

## 🛠️ Troubleshooting

### Google OAuth Issues

**Error: "redirect_uri_mismatch"**
- Add exact URI to Google Console authorized redirect URIs
- Must match exactly: http://localhost:7860/api/v1/oauth/google/callback

**Error: "Google OAuth is not configured"**
- Check LANGFLOW_GOOGLE_CLIENT_ID is set
- Check LANGFLOW_GOOGLE_CLIENT_SECRET is set
- Restart server after setting variables

**User not created**
- Check database migrations: `uv run alembic current`
- Check logs for errors
- Verify NEW_USER_IS_ACTIVE=true

### Phantom Issues

**"Phantom Wallet Not Found"**
- Install Phantom extension
- Refresh page after installation

**Signature verification fails**
- Check Phantom is connected to correct network
- Try disconnecting and reconnecting wallet

**User created but can't login**
- Check oauth_provider='phantom' in database
- Check wallet_address matches

---

## 📈 Next Steps

### Enhance Security (Optional)

1. **Add Email Verification**
   - Send verification email after Google OAuth
   - Store verified_email flag in database

2. **Add 2FA**
   - Implement TOTP for password users
   - OAuth users already have provider 2FA

3. **Session Management**
   - Add active sessions table
   - Allow users to view/revoke sessions

### Enhance UX (Optional)

1. **Profile Pictures**
   - Fetch from Google profile
   - Display in UI

2. **Account Linking**
   - Allow linking Google + Phantom to same account
   - Merge OAuth and password accounts

3. **Social Features**
   - Display "Sign in with Google" count
   - Show last login method

---

## 🎉 You're Done!

Your Langflow now has production-ready OAuth authentication with:
- ✅ Google Sign-In
- ✅ Phantom Wallet Sign-In
- ✅ Multi-tenant data isolation
- ✅ PostgreSQL backend
- ✅ Secure JWT authentication
- ✅ Beautiful UI with branded buttons

Users can now sign in with one click using their Google account or Phantom wallet!

---

## 📞 Support

- **Google OAuth Issues**: Check [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- **Phantom Issues**: Check [Phantom Documentation](https://docs.phantom.app/)
- **Langflow Issues**: Check server logs in `logs/langflow.log`
