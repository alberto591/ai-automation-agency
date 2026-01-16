# Environment Variables Reference

> [!IMPORTANT]
> **Complete reference for all environment variables used in Agenzia AI**
>
> This document lists every environment variable, where it's used, and where it needs to be configured across all deployment platforms.

## Quick Reference by Platform

| Platform | Configuration Location | Documentation |
|----------|----------------------|---------------|
| **Vercel** (Frontend & API) | Project Settings → Environment Variables | [Vercel Docs](https://vercel.com/docs/environment-variables) |
| **Render** (Backend Service) | Dashboard → Environment | [Render Docs](https://render.com/docs/environment-variables) |
| **Railway** (Alternative Backend) | Project → Variables | [Railway Docs](https://docs.railway.app/develop/variables) |
| **Local Development** | `.env` file in project root | Copy from `.env.example` |

---

## Environment Variables by Category

### 🗄️ Database (Supabase)

#### Backend & API

| Variable | Required | Description | Used In |
|----------|----------|-------------|---------|
| `SUPABASE_URL` | ✅ Yes | Supabase project URL | Backend, API, Scripts |
| `SUPABASE_KEY` | ✅ Yes | Supabase anon/public key | Backend, API, Scripts |
| `SUPABASE_SERVICE_ROLE_KEY` | ⚠️ Optional | Admin key for server-side operations | Scripts, Migrations |
| `SUPABASE_JWT_SECRET` | ⚠️ Optional | JWT verification secret | Auth validation |

**Example**:
```bash
SUPABASE_URL=https://zozgvcdnkwtyioyazgmx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=your-jwt-secret
```

**Where to Configure**:
- ✅ Vercel: Project Settings → Environment Variables
- ✅ Render: Dashboard → Environment
- ✅ Railway: Project → Variables
- ✅ Local: `.env` file

**Files Using These**:
- [`config/settings.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/config/settings.py#L6-L10)
- [`infrastructure/adapters/supabase_adapter.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/infrastructure/adapters/supabase_adapter.py)
- All scripts in `scripts/` directory

---

#### Frontend (Dashboard)

| Variable | Required | Description | Used In |
|----------|----------|-------------|---------|
| `VITE_SUPABASE_URL` | ✅ Yes | Supabase URL for Vite frontend | Dashboard app |
| `VITE_SUPABASE_ANON_KEY` | ✅ Yes | Supabase anon key for Vite frontend | Dashboard app |

**Example**:
```bash
VITE_SUPABASE_URL=https://zozgvcdnkwtyioyazgmx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Where to Configure**:
- ✅ Vercel (Dashboard): Project Settings → Environment Variables
- ✅ Local: `apps/dashboard/.env`

**Files Using These**:
- [`apps/dashboard/src/lib/supabase.js`](file:///Users/lycanbeats/Desktop/agenzia-ai/apps/dashboard/src/lib/supabase.js)

---

#### Frontend (Landing Page)

| Variable | Required | Description | Used In |
|----------|----------|-------------|---------|
| `SUPABASE_URL` | ✅ Yes | Supabase URL for landing page | Landing page auth |
| `SUPABASE_ANON_KEY` | ✅ Yes | Supabase anon key for landing page | Landing page auth |

**Example**:
```bash
SUPABASE_URL=https://zozgvcdnkwtyioyazgmx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Where to Configure**:
- ✅ Vercel (Landing Page): Build command must run `scripts/generate-config.sh`
- ✅ Local: Run `scripts/generate-config.sh` to generate `apps/landing-page/config.js`

**Files Using These**:
- [`apps/landing-page/config.js`](file:///Users/lycanbeats/Desktop/agenzia-ai/apps/landing-page/config.js) (generated)
- [`apps/landing-page/auth-helper.js`](file:///Users/lycanbeats/Desktop/agenzia-ai/apps/landing-page/auth-helper.js)

---

### 🤖 AI & LLM Services

#### Mistral AI

| Variable | Required | Description | Used In |
|----------|----------|-------------|---------|
| `MISTRAL_API_KEY` | ✅ Yes | Mistral AI API key | LLM adapter, embeddings |
| `MISTRAL_MODEL` | ⚠️ Optional | Model name (default: `mistral-large-latest`) | LLM adapter |
| `MISTRAL_EMBEDDING_MODEL` | ⚠️ Optional | Embedding model (default: `mistral-embed`) | Embeddings |

**Example**:
```bash
MISTRAL_API_KEY=2sUVLqiwZ18PSk4Q1rfuHMoBaOfSuIdc
MISTRAL_MODEL=mistral-large-latest
MISTRAL_EMBEDDING_MODEL=mistral-embed
```

**Where to Configure**:
- ✅ Vercel: Project Settings → Environment Variables
- ✅ Render: Dashboard → Environment
- ✅ Railway: Project → Variables
- ✅ Local: `.env` file

**Files Using These**:
- [`config/settings.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/config/settings.py#L12-L15)
- `infrastructure/adapters/mistral_adapter.py`

---

#### Perplexity (Research)

| Variable | Required | Description | Used In |
|----------|----------|-------------|---------|
| `PERPLEXITY_API_KEY` | ⚠️ Optional | Perplexity API key for research | Research adapter |

**Example**:
```bash
PERPLEXITY_API_KEY=pplx-your-api-key
```

**Where to Configure**:
- ✅ Vercel: Project Settings → Environment Variables
- ✅ Render: Dashboard → Environment
- ✅ Local: `.env` file

**Files Using These**:
- [`config/settings.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/config/settings.py#L17-L18)
- `infrastructure/adapters/perplexity_adapter.py`

---

#### Deepgram (Voice Transcription)

| Variable | Required | Description | Used In |
|----------|----------|-------------|---------|
| `DEEPGRAM_API_KEY` | ⚠️ Optional | Deepgram API key for voice transcription | Voice adapter |

**Example**:
```bash
DEEPGRAM_API_KEY=your-deepgram-api-key
```

**Where to Configure**:
- ✅ Vercel: Project Settings → Environment Variables
- ✅ Render: Dashboard → Environment
- ✅ Local: `.env` file

**Files Using These**:
- [`config/settings.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/config/settings.py#L20-L21)

---

### 💬 Messaging (WhatsApp)

#### Provider Selection

| Variable | Required | Description | Used In |
|----------|----------|-------------|---------|
| `WHATSAPP_PROVIDER` | ✅ Yes | WhatsApp provider: `twilio` or `meta` | Message routing |

**Example**:
```bash
WHATSAPP_PROVIDER=twilio
```

---

#### Twilio

| Variable | Required | Description | Used In |
|----------|----------|-------------|---------|
| `TWILIO_ACCOUNT_SID` | ✅ Yes (if using Twilio) | Twilio account SID | Twilio adapter |
| `TWILIO_AUTH_TOKEN` | ✅ Yes (if using Twilio) | Twilio auth token | Twilio adapter |
| `TWILIO_PHONE_NUMBER` | ✅ Yes (if using Twilio) | Twilio WhatsApp number (format: `whatsapp:+1234567890`) | Twilio adapter |

**Example**:
```bash
TWILIO_ACCOUNT_SID=AC09c132dca2223eb439efd2ecfa330cb7
TWILIO_AUTH_TOKEN=fdbed349166258246818a40881851d16
TWILIO_PHONE_NUMBER=whatsapp:+34625852546
```

**Where to Configure**:
- ✅ Vercel: Project Settings → Environment Variables
- ✅ Render: Dashboard → Environment
- ✅ Railway: Project → Variables
- ✅ Local: `.env` file

**Files Using These**:
- [`config/settings.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/config/settings.py#L29-L32)
- [`infrastructure/adapters/twilio_adapter.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/infrastructure/adapters/twilio_adapter.py)
- [`scripts/follow_up.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/scripts/follow_up.py)

---

#### Meta Cloud API

| Variable | Required | Description | Used In |
|----------|----------|-------------|---------|
| `META_ACCESS_TOKEN` | ✅ Yes (if using Meta) | Meta WhatsApp Business API access token | Meta adapter |
| `META_PHONE_ID` | ✅ Yes (if using Meta) | Meta phone number ID | Meta adapter |
| `FACEBOOK_VERIFY_TOKEN` | ⚠️ Optional | Webhook verification token | Webhook validation |
| `FACEBOOK_APP_SECRET` | ⚠️ Optional | Facebook app secret for signature validation | Webhook security |

**Example**:
```bash
META_ACCESS_TOKEN=your_meta_access_token
META_PHONE_ID=your_meta_phone_number_id
FACEBOOK_VERIFY_TOKEN=your_verify_token
FACEBOOK_APP_SECRET=your_app_secret
```

**Where to Configure**:
- ✅ Vercel: Project Settings → Environment Variables
- ✅ Render: Dashboard → Environment
- ✅ Railway: Project → Variables
- ✅ Local: `.env` file

**Files Using These**:
- [`config/settings.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/config/settings.py#L34-L38)
- `infrastructure/adapters/meta_whatsapp_adapter.py`

---

### 📅 Calendar & Booking

#### Cal.com

| Variable | Required | Description | Used In |
|----------|----------|-------------|---------|
| `CALCOM_API_KEY` | ✅ Yes | Cal.com API key | Calendar adapter |
| `CALCOM_EVENT_TYPE_ID` | ✅ Yes | Cal.com event type ID | Booking creation |
| `CALCOM_WEBHOOK_SECRET` | ⚠️ Optional | Webhook signature validation | Webhook security |
| `CALCOM_BOOKING_LINK` | ⚠️ Optional | Public booking link (default: `https://cal.com/anzevino-ai`) | Frontend display |

**Example**:
```bash
CALCOM_API_KEY=cal_live_92175cd01777214c0de9a94cacc147cd
CALCOM_EVENT_TYPE_ID=4268371
CALCOM_WEBHOOK_SECRET=18cc650df214a37385324e363a771dc63fa7803ed224d9e1fbeac04b20ec23b2
CALCOM_BOOKING_LINK=https://cal.com/anzevino-ai
```

**Where to Configure**:
- ✅ Vercel: Project Settings → Environment Variables
- ✅ Render: Dashboard → Environment
- ✅ Railway: Project → Variables
- ✅ Local: `.env` file

**Files Using These**:
- [`config/settings.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/config/settings.py#L54-L58)
- `infrastructure/adapters/calcom_adapter.py`

---

#### Google Calendar

| Variable | Required | Description | Used In |
|----------|----------|-------------|---------|
| `GOOGLE_CALENDAR_ID` | ⚠️ Optional | Google Calendar ID | Google Calendar adapter |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | ⚠️ Optional | Google service account JSON (as string) | Google Calendar adapter |

**Example**:
```bash
GOOGLE_CALENDAR_ID=your-calendar-id@group.calendar.google.com
GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account","project_id":"..."}'
```

**Where to Configure**:
- ✅ Vercel: Project Settings → Environment Variables
- ✅ Render: Dashboard → Environment
- ✅ Railway: Project → Variables
- ✅ Local: `.env` file

**Files Using These**:
- [`config/settings.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/config/settings.py#L51-L53)
- [`infrastructure/adapters/google_calendar_adapter.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/infrastructure/adapters/google_calendar_adapter.py)

---

### 📊 Google Sheets Integration

| Variable | Required | Description | Used In |
|----------|----------|-------------|---------|
| `GOOGLE_SHEET_ID` | ⚠️ Optional | Google Sheet ID for lead sync | Google Sheets adapter |
| `GOOGLE_SHEETS_CREDENTIALS_JSON` | ⚠️ Optional | Google service account JSON (as string) | Google Sheets adapter |

**Example**:
```bash
GOOGLE_SHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
GOOGLE_SHEETS_CREDENTIALS_JSON='{"type":"service_account","project_id":"..."}'
```

**Where to Configure**:
- ✅ Vercel: Project Settings → Environment Variables
- ✅ Render: Dashboard → Environment
- ✅ Railway: Project → Variables
- ✅ Local: `.env` file

**Files Using These**:
- [`config/settings.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/config/settings.py#L64-L66)
- [`infrastructure/adapters/google_sheets_adapter.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/infrastructure/adapters/google_sheets_adapter.py)

---

### 🔐 Security & Webhooks

| Variable | Required | Description | Used In |
|----------|----------|-------------|---------|
| `WEBHOOK_API_KEY` | ✅ Yes | API key for webhook authentication | API endpoints |
| `WEBHOOK_BASE_URL` | ⚠️ Optional | Base URL for webhooks | Webhook registration |

**Example**:
```bash
WEBHOOK_API_KEY=prod_dev_secret_key_2025
WEBHOOK_BASE_URL=https://your-api.vercel.app
```

**Where to Configure**:
- ✅ Vercel: Project Settings → Environment Variables
- ✅ Render: Dashboard → Environment
- ✅ Railway: Project → Variables
- ✅ Local: `.env` file

**Files Using These**:
- [`config/settings.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/config/settings.py#L40-L42)
- [`presentation/api/api.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/presentation/api/api.py)

---

### 📧 Email (SMTP)

| Variable | Required | Description | Used In |
|----------|----------|-------------|---------|
| `SMTP_SERVER` | ⚠️ Optional | SMTP server (default: `smtp.gmail.com`) | Email notifications |
| `SMTP_PORT` | ⚠️ Optional | SMTP port (default: `587`) | Email notifications |
| `SMTP_USER` | ⚠️ Optional | SMTP username/email | Email notifications |
| `SMTP_PASSWORD` | ⚠️ Optional | SMTP password/app password | Email notifications |

**Example**:
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

**Where to Configure**:
- ✅ Vercel: Project Settings → Environment Variables
- ✅ Render: Dashboard → Environment
- ✅ Railway: Project → Variables
- ✅ Local: `.env` file

**Files Using These**:
- [`config/settings.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/config/settings.py#L73-L77)
- `infrastructure/adapters/notification_adapter.py`

---

### 📥 Email Ingestion (IMAP)

| Variable | Required | Description | Used In |
|----------|----------|-------------|---------|
| `IMAP_SERVER` | ⚠️ Optional | IMAP server (default: `imap.gmail.com`) | Email ingestion |
| `IMAP_EMAIL` | ⚠️ Optional | IMAP email address | Email ingestion |
| `IMAP_PASSWORD` | ⚠️ Optional | IMAP password/app password | Email ingestion |

**Example**:
```bash
IMAP_SERVER=imap.gmail.com
IMAP_EMAIL=your_email@gmail.com
IMAP_PASSWORD=your_app_password
```

**Where to Configure**:
- ✅ Vercel: Project Settings → Environment Variables
- ✅ Render: Dashboard → Environment
- ✅ Railway: Project → Variables
- ✅ Local: `.env` file

**Files Using These**:
- [`config/settings.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/config/settings.py#L79-L82)

---

### 💳 Stripe (Payments)

| Variable | Required | Description | Used In |
|----------|----------|-------------|---------|
| `STRIPE_SECRET_KEY` | ⚠️ Optional | Stripe secret key | Payment processing |
| `STRIPE_CONNECT_CLIENT_ID` | ⚠️ Optional | Stripe Connect client ID | Multi-tenant payments |
| `BASE_URL` | ⚠️ Optional | Base URL for OAuth redirects | Stripe Connect |

**Example**:
```bash
STRIPE_SECRET_KEY=sk_live_...
STRIPE_CONNECT_CLIENT_ID=ca_...
BASE_URL=https://agenzia-ai.vercel.app
```

**Where to Configure**:
- ✅ Vercel: Project Settings → Environment Variables
- ✅ Render: Dashboard → Environment
- ✅ Railway: Project → Variables
- ✅ Local: `.env` file

**Files Using These**:
- [`config/settings.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/config/settings.py#L84-L87)

---

### 📊 Monitoring & Analytics

#### Sentry

| Variable | Required | Description | Used In |
|----------|----------|-------------|---------|
| `SENTRY_DSN` | ⚠️ Optional | Sentry DSN for error tracking | Error monitoring |
| `ENVIRONMENT` | ⚠️ Optional | Environment name (default: `development`) | Sentry context |

**Example**:
```bash
SENTRY_DSN=https://your-sentry-dsn@sentry.io/your-project-id
ENVIRONMENT=production
```

**Where to Configure**:
- ✅ Vercel: Project Settings → Environment Variables
- ✅ Render: Dashboard → Environment
- ✅ Railway: Project → Variables
- ✅ Local: `.env` file

**Files Using These**:
- [`config/settings.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/config/settings.py#L60-L62)

---

### 🏢 Agency Configuration

| Variable | Required | Description | Used In |
|----------|----------|-------------|---------|
| `AGENCY_OWNER_PHONE` | ✅ Yes | Agency owner phone for notifications | Notifications |
| `AGENCY_OWNER_EMAIL` | ✅ Yes | Agency owner email for notifications | Notifications |
| `DEFAULT_TENANT_ID` | ⚠️ Optional | Default tenant ID for multi-tenancy | Multi-tenant routing |

**Example**:
```bash
AGENCY_OWNER_PHONE=+34625852546
AGENCY_OWNER_EMAIL=albertocalvorivas@gmail.com
DEFAULT_TENANT_ID=tenant-uuid
```

**Where to Configure**:
- ✅ Vercel: Project Settings → Environment Variables
- ✅ Render: Dashboard → Environment
- ✅ Railway: Project → Variables
- ✅ Local: `.env` file

**Files Using These**:
- [`config/settings.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/config/settings.py#L68-L71)

---

### 🔧 External APIs

#### RapidAPI (Idealista Market Data)

| Variable | Required | Description | Used In |
|----------|----------|-------------|---------|
| `RAPIDAPI_KEY` | ⚠️ Optional | RapidAPI key for Idealista data | Market scraper |

**Example**:
```bash
RAPIDAPI_KEY=cc5d558de1mshc69ef5edc8bc40dp1cb57ajsn60e09f9852b9
```

**Where to Configure**:
- ✅ Vercel: Project Settings → Environment Variables
- ✅ Render: Dashboard → Environment
- ✅ Railway: Project → Variables
- ✅ Local: `.env` file

**Files Using These**:
- [`config/settings.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/config/settings.py#L89-L90)
- `infrastructure/market_scraper.py`

---

### 🧪 Testing & Development

| Variable | Required | Description | Used In |
|----------|----------|-------------|---------|
| `TEST_MODE` | ⚠️ Optional | Enable test mode (default: `false`) | Development |
| `REDIS_URL` | ⚠️ Optional | Redis connection URL | Caching |

**Example**:
```bash
TEST_MODE=false
REDIS_URL=redis://localhost:6379/0
```

**Where to Configure**:
- ✅ Local: `.env` file only
- ❌ Do NOT set `TEST_MODE=true` in production

**Files Using These**:
- [`config/settings.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/config/settings.py#L92-L95)

---

## Platform-Specific Configuration

### Vercel (Frontend & API)

**Location**: [Vercel Dashboard](https://vercel.com) → Your Project → Settings → Environment Variables

**Required Variables**:
```bash
# Database
SUPABASE_URL=https://zozgvcdnkwtyioyazgmx.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_ANON_KEY=your-anon-key  # For landing page config generation

# AI
MISTRAL_API_KEY=your-mistral-key

# Messaging
WHATSAPP_PROVIDER=twilio
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=whatsapp:+1234567890

# Calendar
CALCOM_API_KEY=your-calcom-key
CALCOM_EVENT_TYPE_ID=your-event-id

# Security
WEBHOOK_API_KEY=your-webhook-key

# Agency
AGENCY_OWNER_PHONE=+1234567890
AGENCY_OWNER_EMAIL=your@email.com
```

**Build Command Update**:
```json
{
  "buildCommand": "bash scripts/generate-config.sh && npm run build"
}
```

---

### Render (Backend Service)

**Location**: [Render Dashboard](https://render.com) → Your Service → Environment

**Required Variables**: Same as Vercel, plus:
```bash
# Additional for backend
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
ENVIRONMENT=production
```

---

### Railway (Alternative Backend)

**Location**: [Railway Dashboard](https://railway.app) → Your Project → Variables

**Required Variables**: Same as Render

---

## Security Best Practices

> [!CAUTION]
> **Never commit these files to git**:
> - `.env`
> - `.env.local`
> - `.env.production`
> - `apps/landing-page/config.js`
> - `dist/config.js`

### Rotating Credentials

When rotating credentials (recommended after making repository public):

1. **Supabase Keys**:
   - Go to Supabase Dashboard → Settings → API
   - Generate new anon key
   - Update `SUPABASE_KEY` and `SUPABASE_ANON_KEY` everywhere

2. **Twilio**:
   - Go to Twilio Console → Account → API Keys
   - Create new API key
   - Update `TWILIO_AUTH_TOKEN`

3. **Google Service Accounts**:
   - Go to Google Cloud Console → IAM & Admin → Service Accounts
   - Create new key for service account
   - Update `GOOGLE_SERVICE_ACCOUNT_JSON` and `GOOGLE_SHEETS_CREDENTIALS_JSON`

4. **Other APIs**:
   - Mistral, Perplexity, Deepgram, Cal.com: Regenerate keys in respective dashboards

---

## Verification Checklist

Before deploying to production:

- [ ] All required variables set in Vercel
- [ ] All required variables set in Render/Railway
- [ ] Build command includes `scripts/generate-config.sh` for landing page
- [ ] `.env.example` is up to date
- [ ] No hardcoded credentials in code
- [ ] `config.js` is in `.gitignore`
- [ ] Test deployment with new environment variables
- [ ] Verify WhatsApp messaging works
- [ ] Verify calendar booking works
- [ ] Verify database connections work
