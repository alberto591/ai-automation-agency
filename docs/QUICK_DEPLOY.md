# Final Deployment Guide

## Current Status
✅ **Production Ready** - All verification complete

## Quick Deploy Checklist

### 1. Verify Local Setup ✅
```bash
# Landing page running on port 5173
npm run dev  # Already running (13h+)

# API health check
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### 2. Final Code Push
```bash
# Verify clean state
git status

# All recent changes already pushed:
# - Commit cde3673: UI fixes, testing, demo improvements
# - Commit 3dea89e: ADRs & lint fixes
# - Commit 9553638: PLC0415 config fix
```

### 3. Vercel Deployment

**Auto-Deploy**: Vercel deploys automatically on push to master

**Manual Trigger** (if needed):
1. Go to Vercel dashboard
2. Select project
3. Click "Deploy" for latest commit

**Environment Variables** (verify these are set):
- Landing Page:
  - `VITE_API_URL` → Your production API URL

- Dashboard:
  - `VITE_SUPABASE_URL`
  - `VITE_SUPABASE_ANON_KEY`
  - `VITE_API_URL`

### 4. Backend Deployment (Render/Railway)

**Start Command**:
```bash
uvicorn presentation.api.api:app --host 0.0.0.0 --port $PORT
```

**Environment Variables** (verify all are set):
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `MISTRAL_API_KEY`
- `MISTRAL_MODEL`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`
- `WEBHOOK_API_KEY`

### 5. Post-Deploy Verification

```bash
# Test production API
curl https://your-api.onrender.com/health

# Test appraisal form
# Navigate to: https://your-site.vercel.app/appraisal/?lang=it
# Fill form and submit

# Test demo script against production
API_URL=https://your-api.onrender.com python scripts/live_demo.py
# Select scenario 4
```

## Optional: Production Data

**If you need fresh property data**:
```bash
# Requires RAPIDAPI_KEY in .env
python scripts/gather_production_data.py

# Runs for 30 minutes, scrapes:
# - Milano Centro, Navigli, Isola
# - Firenze Centro
# - Chianti, Toscana
```

## Monitoring

**After deployment, monitor**:
1. Vercel deployment logs
2. Render/Railway application logs
3. Sentry error tracking (if configured)
4. Test WhatsApp integration with real number

## Rollback Plan

**If issues arise**:
```bash
# Revert to previous commit
git revert HEAD
git push origin master

# Or manually deploy previous version in Vercel/Render
```

## Support Contacts

- **Frontend**: Vercel dashboard
- **Backend**: Render/Railway dashboard
- **Database**: Supabase dashboard
- **Messaging**: Twilio console

---

**Last Verified**: January 2, 2026, 15:47 CET
**Version**: All systems go ✅
