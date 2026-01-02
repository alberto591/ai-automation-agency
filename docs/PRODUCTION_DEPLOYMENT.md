# 🚀 Production Deployment Guide: Agency CRM Dashboard

This document details the exact steps and environment variables required to deploy your Agency AI system to production.

## 🏗️ Architecture Overview
*   **Frontend Dashboard**: React + Vite (in `dashboard/`) → Deployed on **Vercel**.
*   **Landing Page**: Static site (in `apps/landing-page/`) → Deployed on **Vercel** or **Netlify**.
*   **Backend API**: Python FastAPI (in `/`) → Deployed on **Render** (or Railway).
*   **Database**: Supabase (PostgreSQL + Realtime + Vector Search).
*   **Messaging**: Twilio WhatsApp Sandbox/Production.

---

## 🎨 Part 1: Frontend Deployment (Vercel)

### Dashboard
1.  **Vercel Project Setup**:
    *   Connect your GitHub Repo: `ai-automation-agency`.
    *   **Root Directory**: Set this to `dashboard`. (Very Important!)
    *   **Framework Preset**: Vite.
2.  **Environment Variables**: Add these in the Vercel Project Settings:
    *   `VITE_SUPABASE_URL`: `https://zozgvcdnkwtyioyazgmx.supabase.co`
    *   `VITE_SUPABASE_ANON_KEY`: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpvemd2Y2Rua3d0eWlveWF6Z214Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzU1MjMsImV4cCI6MjA4MTY1MTUyM30.Z-IsY7vYkwIo6sB22ZpGIMTFD9kXSRdO6Ykv_bXwOvg`
    *   `VITE_API_URL`: Use your Backend URL from Part 2.
3.  **Deployment**: Click \"Deploy\". Your site will be live at `https://your-project.vercel.app`.

### Landing Page (Appraisal Tool)
1.  **Vercel Project Setup** (or Netlify):
    *   **Root Directory**: `apps/landing-page`
    *   **Build Command**: `npm run build`
    *   **Output Directory**: `dist`
2.  **Environment Variables**:
    *   `VITE_API_URL`: Your backend API URL
3.  **Deployment**: The appraisal form will be available at `/appraisal/`

---

## 🐍 Part 2: Backend Deployment (Render / Railway)

1.  **New Web Service**: Connect the same GitHub repo.
2.  **Runtime**: Python.
3.  **Build Command**: `pip install -r requirements.txt`
4.  **Start Command**: `uvicorn presentation.api.api:app --host 0.0.0.0 --port $PORT`
5.  **Environment Variables**: Add these in Render's \"Environment\" tab:
    *   `SUPABASE_URL`: `https://zozgvcdnkwtyioyazgmx.supabase.co`
    *   `SUPABASE_KEY`: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpvemd2Y2Rua3d0eWlveWF6Z214Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzU1MjMsImV4cCI6MjA4MTY1MTUyM30.Z-IsY7vYkwIo6sB22ZpGIMTFD9kXSRdO6Ykv_bXwOvg`
    *   `MISTRAL_API_KEY`: `2sUVLqiwZ18PSk4Q1rfuHMoBaOfSuIdc`
    *   `MISTRAL_MODEL`: `mistral-large-latest`
    *   `TWILIO_ACCOUNT_SID`: `AC09c132dca2223eb439efd2ecfa330cb7`
    *   `TWILIO_AUTH_TOKEN`: `fdbed349166258246818a40881851d16`
    *   `TWILIO_PHONE_NUMBER`: `whatsapp:+14155238886`
    *   `WEBHOOK_API_KEY`: `prod_dev_secret_key_2025`
    *   `PERPLEXITY_API_KEY`: (Your key for market research)

---

## 🔗 Part 3: Linking & Final Updates

1.  **Update Vercel**: Once your Render backend is live (e.g., `https://my-api.onrender.com`), update your Vercel `VITE_API_URL` environment variable and **Redeploy**.
2.  **Twilio Webhook**: Go to [Twilio Console](https://console.twilio.com) → Messaging → Try it Out → WhatsApp Sandbox Settings.
    *   Update **\"When a message comes in\"** to: `https://your-backend-url.com/api/webhooks/twilio`
3.  **Appraisal Hook**: The landing page appraisal form hits `/api/appraisals/estimate` - ensure CORS is configured.

---

## ✅ Pre-Deployment Testing

Before deploying to production, run the test suite:

```bash
# Unit tests (should have 138/141 passing minimum)
pytest tests/unit/ -v

# Test appraisal flow
python scripts/live_demo.py
# Select scenario 4 and verify investment metrics
```

---

## 🛠️ Local Maintenance

### Dashboard
If you need to update the dashboard locally:
1. `cd dashboard`
2. `npm install`
3. `npm run dev`

### Landing Page
For the landing page:
1. `cd apps/landing-page`
2. `npm install`
3. `npm run dev`

---

## 🎯 Post-Deployment Verification

1. **Test Appraisal UI**: Navigate to `/appraisal/?lang=it` and submit a test property
2. **Check API Health**: `curl https://your-api.com/health` should return `{"status": "healthy"}`
3. **Verify WhatsApp**: Send a message to your Twilio number
4. **Run Live Demo**: Use `scripts/live_demo.py` against production URL
