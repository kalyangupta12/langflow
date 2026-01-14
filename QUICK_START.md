# 🚀 QUICK REFERENCE - Langflow Multi-Tenant Setup

## ✅ COMPLETED SETUP

### 1. DATABASE: PostgreSQL (Supabase)
```
Connection: ✓ Active
Host: aws-1-ap-south-1.pooler.supabase.com:6543
Database: postgres
```

### 2. AUTHENTICATION: Enabled
```
Auto-Login: DISABLED
Admin Username: admin
Admin Password: SecureAdmin@2026
```

### 3. SERVER
```
URL: http://127.0.0.1:7860
Status: Running
Multi-Tenant: ✓ Enabled
```

---

## 🔑 LOGIN NOW

1. Open: **http://127.0.0.1:7860**
2. Login:
   - **Username**: `admin`
   - **Password**: `SecureAdmin@2026`
3. **CHANGE PASSWORD** in Settings immediately!

---

## 👥 CREATE USERS

### Via Web UI:
1. Login as admin
2. Go to Settings → Users
3. Click "Add User"
4. Activate user account

### Via API:
```bash
curl -X POST http://127.0.0.1:7860/api/v1/users/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "username": "newuser@example.com",
    "password": "SecurePass123!",
    "is_active": true
  }'
```

---

## 🔐 OAUTH SETUP (Next Steps)

### Option 1: Supabase Auth (RECOMMENDED)
Since you're already using Supabase PostgreSQL:

1. **Enable Auth in Supabase**:
   ```
   Dashboard: https://supabase.com/dashboard/project/fgsksclhdanmgylswifm/auth
   ```

2. **Enable Google OAuth**:
   - Go to Auth → Providers → Google
   - Add Google Client ID/Secret from Google Cloud Console
   - Set redirect URL: `http://127.0.0.1:7860/api/v1/auth/callback`

3. **Frontend Integration**:
   ```javascript
   import { createClient } from '@supabase/supabase-js'
   
   const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)
   
   // Google login
   await supabase.auth.signInWithOAuth({
     provider: 'google'
   })
   ```

### Option 2: Auth0 / Clerk
- Faster setup
- More providers out-of-box
- Managed infrastructure

### Option 3: Custom Implementation
- Full control
- See SETUP_GUIDE.md for code examples

---

## 🎯 MULTI-TENANT FEATURES

Each user automatically gets:
- ✅ Isolated workspace
- ✅ Personal flows & folders
- ✅ Separate API keys
- ✅ Private variables & credentials
- ✅ Individual usage tracking

---

## ⚠️ IMPORTANT SECURITY

### DO NOW:
1. ✅ Change admin password
2. ✅ Enable HTTPS for production
3. ✅ Set up database backups (Supabase does this automatically)
4. ✅ Configure environment variables properly

### .env Configuration:
```env
# Database (✓ Configured)
LANGFLOW_DATABASE_URL=postgresql://...

# Auth (✓ Configured)
LANGFLOW_AUTO_LOGIN=false
LANGFLOW_SUPERUSER=admin
LANGFLOW_SUPERUSER_PASSWORD=SecureAdmin@2026  # CHANGE THIS!

# For OAuth (To be added):
# GOOGLE_CLIENT_ID=...
# GOOGLE_CLIENT_SECRET=...
# PHANTOM_APP_URL=...
```

---

## 🔧 MANAGE SERVER

### Start Server:
```powershell
cd e:\langflow\langflow
$env:Path = "C:\Users\new\.local\bin;$env:Path"
uv run langflow run --host 127.0.0.1 --port 7860
```

### Stop Server:
```powershell
Get-Process -Name python | Where-Object {$_.CommandLine -like "*langflow*"} | Stop-Process
```

### View Logs:
```powershell
Get-Content logs/langflow.log -Tail 50 -Wait
```

### Test Database:
```powershell
uv run python -c "from langflow.services.database.utils import initialize_database; print('DB OK')"
```

---

## 📊 DATABASE ACCESS

### Supabase Dashboard:
```
https://supabase.com/dashboard/project/fgsksclhdanmgylswifm
```

### Direct SQL Access:
```sql
-- View users
SELECT id, username, is_active, is_superuser, created_at FROM "user";

-- View user flows
SELECT u.username, f.name, f.created_at 
FROM flow f 
JOIN "user" u ON f.user_id = u.id;

-- User statistics
SELECT 
  u.username,
  COUNT(DISTINCT f.id) as flow_count,
  COUNT(DISTINCT a.id) as api_key_count
FROM "user" u
LEFT JOIN flow f ON u.id = f.user_id
LEFT JOIN apikey a ON u.id = a.user_id
GROUP BY u.username;
```

---

## 🐛 TROUBLESHOOTING

### Can't Login?
```bash
# Reset admin password
uv run langflow superuser --username admin --password NewPass123
```

### Database Issues?
```bash
# Check connection
uv run python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://...'); print(engine.connect())"

# Check Supabase status
# Visit: https://status.supabase.com/
```

### Server Not Starting?
```bash
# Check logs
cat logs/langflow.log

# Check port availability
netstat -ano | findstr :7860

# Restart with debug
uv run langflow run --log-level debug
```

---

## 📚 DOCUMENTATION

- **Full Setup Guide**: `SETUP_GUIDE.md`
- **Langflow Docs**: https://docs.langflow.org
- **Supabase Docs**: https://supabase.com/docs
- **API Reference**: http://127.0.0.1:7860/docs

---

## ✨ STATUS SUMMARY

```
Database:        ✅ PostgreSQL (Supabase)
Authentication:  ✅ Manual Login Enabled
Multi-Tenant:    ✅ Active (Per-User Isolation)
OAuth Google:    ⚠️  Needs Implementation
OAuth Phantom:   ⚠️  Needs Implementation
Server:          ✅ Running on :7860
```

**Your Langflow is now running with PostgreSQL and multi-tenant architecture!**

**Next Step**: Login at http://127.0.0.1:7860 and change the admin password.

For OAuth integration, see `SETUP_GUIDE.md` for detailed implementation options.
