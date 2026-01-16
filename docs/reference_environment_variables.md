# Environment Variables Setup Checklist

> [!IMPORTANT]
> **Complete checklist for configuring all environment variables across deployment platforms**
>
> Use this document to ensure all required environment variables are properly configured in Vercel, Render, and local development.

---

## Quick Platform Links

- **Vercel**: [Dashboard](https://vercel.com) → Your Project → Settings → Environment Variables
- **Render**: [Dashboard](https://render.com) → Your Service → Environment

- **Local**: `.env` file in project root (copy from `.env.example`)

---

## Setup Tasks by Platform

### ☁️ Vercel (Frontend & API)

#### Core Database (Required)
- [ ] Set `SUPABASE_URL` = `https://your-project.supabase.co`
- [ ] Set `SUPABASE_KEY` = Your Supabase anon key
- [ ] Set `SUPABASE_ANON_KEY` = Same as SUPABASE_KEY (for landing page)
- [ ] Set `VITE_SUPABASE_URL` = Same as SUPABASE_URL (for dashboard)
- [ ] Set `VITE_SUPABASE_ANON_KEY` = Same as SUPABASE_KEY (for dashboard)

#### AI Services (Required)
- [ ] Set `MISTRAL_API_KEY` = Your Mistral AI API key

#### Messaging - Twilio (Required if using Twilio)
- [ ] Set `WHATSAPP_PROVIDER` = `twilio`
- [ ] Set `TWILIO_ACCOUNT_SID` = Your Twilio account SID
- [ ] Set `TWILIO_AUTH_TOKEN` = Your Twilio auth token
- [ ] Set `TWILIO_PHONE_NUMBER` = `whatsapp:+1234567890` (or your number)

#### Messaging - Meta (Alternative to Twilio)
- [ ] Set `WHATSAPP_PROVIDER` = `meta`
- [ ] Set `META_ACCESS_TOKEN` = Your Meta access token
- [ ] Set `META_PHONE_ID` = Your Meta phone number ID

#### Calendar & Booking (Required)
- [ ] Set `CALCOM_API_KEY` = Your Cal.com API key
- [ ] Set `CALCOM_EVENT_TYPE_ID` = Your Cal.com event type ID
- [ ] Set `CALCOM_WEBHOOK_SECRET` = Your Cal.com webhook secret
- [ ] Set `CALCOM_BOOKING_LINK` = `https://cal.com/anzevino-ai`

#### Security (Required)
- [ ] Set `WEBHOOK_API_KEY` = Your webhook API key (e.g., `prod_dev_secret_key_2025`)

#### Agency Configuration (Required)
- [ ] Set `AGENCY_OWNER_PHONE` = `+1234567890` (or your phone)
- [ ] Set `AGENCY_OWNER_EMAIL` = `your-email@example.com` (or your email)

#### Google Services (Optional)
- [ ] Set `GOOGLE_CALENDAR_ID` = Your Google Calendar ID
- [ ] Set `GOOGLE_SERVICE_ACCOUNT_JSON` = Your Google service account JSON (as string)
- [ ] Set `GOOGLE_SHEET_ID` = Your Google Sheet ID
- [ ] Set `GOOGLE_SHEETS_CREDENTIALS_JSON` = Your Google Sheets credentials JSON

#### Additional AI Services (Optional)
- [ ] Set `PERPLEXITY_API_KEY` = Your Perplexity API key
- [ ] Set `DEEPGRAM_API_KEY` = Your Deepgram API key

#### Email/SMTP (Optional)
- [ ] Set `SMTP_SERVER` = `smtp.gmail.com`
- [ ] Set `SMTP_PORT` = `587`
- [ ] Set `SMTP_USER` = Your email address
- [ ] Set `SMTP_PASSWORD` = Your email app password

#### Monitoring (Optional)
- [ ] Set `SENTRY_DSN` = Your Sentry DSN
- [ ] Set `ENVIRONMENT` = `production`

#### External APIs (Optional)
- [ ] Set `RAPIDAPI_KEY` = Your RapidAPI key (for Idealista data)
- [ ] Set `STRIPE_SECRET_KEY` = Your Stripe secret key
- [ ] Set `STRIPE_CONNECT_CLIENT_ID` = Your Stripe Connect client ID

#### Build Configuration
- [ ] Update build command to include: `bash scripts/generate-config.sh && <your-build-command>`
- [ ] Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` are set (needed for config generation)

---

### �️ Supabase (Database Platform)

#### Project Settings
- [ ] Navigate to [Supabase Dashboard](https://app.supabase.com) → Your Project

#### Database Configuration
- [ ] Verify database is created and active
- [ ] Note your project URL: `https://[project-ref].supabase.co`
- [ ] Go to Settings → API to get your keys

#### API Keys (Copy these to other platforms)
- [ ] Copy `Project URL` → Use as `SUPABASE_URL`
- [ ] Copy `anon/public` key → Use as `SUPABASE_KEY` and `SUPABASE_ANON_KEY`
- [ ] Copy `service_role` key → Use as `SUPABASE_SERVICE_ROLE_KEY` (keep secret!)

#### Authentication Settings
- [ ] Go to Authentication → URL Configuration
- [ ] Set Site URL: `https://your-domain.vercel.app`
- [ ] Add Redirect URLs:
  - [ ] `https://your-domain.vercel.app/login.html`
  - [ ] `https://your-domain.vercel.app/reset-password.html`
  - [ ] `http://localhost:5174/login.html` (for local dashboard)

#### Row Level Security (RLS)
- [ ] Go to Database → Tables
- [ ] Verify RLS is enabled on all tables with sensitive data
- [ ] Review RLS policies for `leads`, `conversations`, `messages` tables
- [ ] Ensure tenant isolation policies are in place

#### Storage (if using file uploads)
- [ ] Go to Storage → Buckets
- [ ] Create necessary buckets (e.g., `property-images`, `documents`)
- [ ] Set appropriate RLS policies on storage buckets
- [ ] Configure CORS if needed

#### Edge Functions (if using)
- [ ] Go to Edge Functions
- [ ] Deploy any custom edge functions
- [ ] Set environment variables for edge functions

#### Database Migrations
- [ ] Ensure all migrations are applied
- [ ] Check Database → Migrations for status
- [ ] Run any pending migrations from `supabase/migrations/` directory

---

### �🚀 Render (Backend Service)

#### Core Database (Required)
- [ ] Set `SUPABASE_URL` = `https://your-project.supabase.co`
- [ ] Set `SUPABASE_KEY` = Your Supabase anon key
- [ ] Set `SUPABASE_SERVICE_ROLE_KEY` = Your Supabase service role key (for admin operations)
- [ ] Set `SUPABASE_JWT_SECRET` = Your Supabase JWT secret

#### AI Services (Required)
- [ ] Set `MISTRAL_API_KEY` = Your Mistral AI API key
- [ ] Set `MISTRAL_MODEL` = `mistral-large-latest`
- [ ] Set `MISTRAL_EMBEDDING_MODEL` = `mistral-embed`

#### Messaging - Twilio (Required if using Twilio)
- [ ] Set `WHATSAPP_PROVIDER` = `twilio`
- [ ] Set `TWILIO_ACCOUNT_SID` = Your Twilio account SID
- [ ] Set `TWILIO_AUTH_TOKEN` = Your Twilio auth token
- [ ] Set `TWILIO_PHONE_NUMBER` = `whatsapp:+1234567890`

#### Messaging - Meta (Alternative)
- [ ] Set `WHATSAPP_PROVIDER` = `meta`
- [ ] Set `META_ACCESS_TOKEN` = Your Meta access token
- [ ] Set `META_PHONE_ID` = Your Meta phone number ID
- [ ] Set `FACEBOOK_VERIFY_TOKEN` = Your Facebook verify token
- [ ] Set `FACEBOOK_APP_SECRET` = Your Facebook app secret

#### Calendar & Booking (Required)
- [ ] Set `CALCOM_API_KEY` = Your Cal.com API key
- [ ] Set `CALCOM_EVENT_TYPE_ID` = Your Cal.com event type ID
- [ ] Set `CALCOM_WEBHOOK_SECRET` = Your Cal.com webhook secret
- [ ] Set `CALCOM_BOOKING_LINK` = `https://cal.com/anzevino-ai`

#### Security (Required)
- [ ] Set `WEBHOOK_API_KEY` = Your webhook API key
- [ ] Set `WEBHOOK_BASE_URL` = Your API base URL (e.g., `https://agenzia-api.onrender.com`)

#### Agency Configuration (Required)
- [ ] Set `AGENCY_OWNER_PHONE` = `+1234567890`
- [ ] Set `AGENCY_OWNER_EMAIL` = `your-email@example.com`

#### Environment (Required)
- [ ] Set `ENVIRONMENT` = `production`

#### Google Services (Optional)
- [ ] Set `GOOGLE_CALENDAR_ID` = Your Google Calendar ID
- [ ] Set `GOOGLE_SERVICE_ACCOUNT_JSON` = Your Google service account JSON
- [ ] Set `GOOGLE_SHEET_ID` = Your Google Sheet ID
- [ ] Set `GOOGLE_SHEETS_CREDENTIALS_JSON` = Your Google Sheets credentials JSON

#### Additional Services (Optional)
- [ ] Set `PERPLEXITY_API_KEY` = Your Perplexity API key
- [ ] Set `DEEPGRAM_API_KEY` = Your Deepgram API key
- [ ] Set `REDIS_URL` = Your Redis connection URL
- [ ] Set `SENTRY_DSN` = Your Sentry DSN
- [ ] Set `RAPIDAPI_KEY` = Your RapidAPI key
- [ ] Set `SMTP_SERVER` = `smtp.gmail.com`
- [ ] Set `SMTP_PORT` = `587`
- [ ] Set `SMTP_USER` = Your email
- [ ] Set `SMTP_PASSWORD` = Your email app password
- [ ] Set `IMAP_SERVER` = `imap.gmail.com`
- [ ] Set `IMAP_EMAIL` = Your email
- [ ] Set `IMAP_PASSWORD` = Your email app password

---

---

### 💻 Local Development

#### Initial Setup
- [ ] Copy `.env.example` to `.env` in project root
- [ ] Update all placeholder values with real credentials

#### Core Database (Required)
- [ ] Set `SUPABASE_URL` in `.env`
- [ ] Set `SUPABASE_KEY` in `.env`
- [ ] Set `SUPABASE_SERVICE_ROLE_KEY` in `.env` (optional, for scripts)
- [ ] Set `VITE_SUPABASE_URL` in `apps/dashboard/.env`
- [ ] Set `VITE_SUPABASE_ANON_KEY` in `apps/dashboard/.env`

#### Generate Landing Page Config
- [ ] Run: `SUPABASE_URL=<url> SUPABASE_ANON_KEY=<key> bash scripts/generate-config.sh`
- [ ] Verify `apps/landing-page/config.js` was created

#### AI & Messaging (Required)
- [ ] Set `MISTRAL_API_KEY` in `.env`
- [ ] Set `WHATSAPP_PROVIDER` in `.env` (`twilio` or `meta`)
- [ ] Set Twilio or Meta credentials in `.env`

#### Calendar (Required)
- [ ] Set `CALCOM_API_KEY` in `.env`
- [ ] Set `CALCOM_EVENT_TYPE_ID` in `.env`

#### Other Services (Optional)
- [ ] Set any optional services you need (Google, Sentry, etc.)

#### Testing
- [ ] Set `TEST_MODE=false` in `.env` (or `true` for development)

---

## Security Checklist

### Before Making Repository Public
- [ ] Verify no hardcoded credentials in code: `grep -r "eyJ" apps/landing-page/*.js`
- [ ] Verify `.env` files are gitignored: `git ls-files | grep "\.env$"`
- [ ] Verify `config.js` is gitignored: `git check-ignore apps/landing-page/config.js`
- [ ] Review `.env.example` has no real credentials

### After Making Repository Public
- [ ] Rotate Supabase anon key in Supabase Dashboard
- [ ] Update `SUPABASE_KEY` and `SUPABASE_ANON_KEY` in all platforms
- [ ] Consider rotating Twilio auth token
- [ ] Consider rotating Google service account keys
- [ ] Update all deployment platforms with new keys

---

## Verification Checklist

### Vercel Deployment
- [ ] All required environment variables are set
- [ ] Build command includes `scripts/generate-config.sh`
- [ ] Deploy and check for errors
- [ ] Test landing page authentication
- [ ] Test dashboard authentication
- [ ] Verify API endpoints work

### Render Deployment
- [ ] All required environment variables are set
- [ ] Service starts without errors
- [ ] Check logs for missing environment variables
- [ ] Test WhatsApp messaging
- [ ] Test calendar booking
- [ ] Test database connections

### Local Development
- [ ] `.env` file is complete
- [ ] `config.js` generated successfully
- [ ] Backend server starts: `uvicorn presentation.api.api:app --reload`
- [ ] Dashboard runs: `cd apps/dashboard && npm run dev`
- [ ] Landing page works: Open `apps/landing-page/index.html`
- [ ] All integrations work (WhatsApp, Calendar, Database)

---

## Quick Reference: Where Variables Are Used

### Files That Read Environment Variables

**Backend Configuration**:
- [`config/settings.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/config/settings.py) - All backend env vars

**Frontend**:
- [`apps/dashboard/src/lib/supabase.js`](file:///Users/lycanbeats/Desktop/agenzia-ai/apps/dashboard/src/lib/supabase.js) - VITE_SUPABASE_*
- [`apps/landing-page/auth-helper.js`](file:///Users/lycanbeats/Desktop/agenzia-ai/apps/landing-page/auth-helper.js) - window.ENV (from config.js)

**Adapters**:
- [`infrastructure/adapters/supabase_adapter.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/infrastructure/adapters/supabase_adapter.py)
- [`infrastructure/adapters/twilio_adapter.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/infrastructure/adapters/twilio_adapter.py)
- [`infrastructure/adapters/google_calendar_adapter.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/infrastructure/adapters/google_calendar_adapter.py)
- [`infrastructure/adapters/google_sheets_adapter.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/infrastructure/adapters/google_sheets_adapter.py)

**Scripts**:
- All scripts in `scripts/` directory use various env vars

---

## Common Issues & Solutions

### Issue: Landing page shows "Missing Supabase configuration"
**Solution**: Ensure `scripts/generate-config.sh` runs during build and `SUPABASE_URL` + `SUPABASE_ANON_KEY` are set in Vercel

### Issue: WhatsApp messages not sending
**Solution**: Check `WHATSAPP_PROVIDER` is set correctly and corresponding credentials (Twilio or Meta) are configured

### Issue: Calendar bookings fail
**Solution**: Verify `CALCOM_API_KEY` and `CALCOM_EVENT_TYPE_ID` are correct

### Issue: Database connection errors
**Solution**: Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct and Supabase project is active

### Issue: Build fails on Vercel
**Solution**: Ensure build command includes config generation: `bash scripts/generate-config.sh && npm run build`
