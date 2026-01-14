# Railway Deployment Guide for Agenzia AI Backend

## Quick Deploy via Railway Dashboard

Since the Railway CLI is having authentication issues, use the web dashboard instead:

### 1. Create New Project

1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account if not already connected
5. Select the `agenzia-ai` repository
6. Railway will automatically detect the Python application

### 2. Configure Environment Variables

In the Railway dashboard, go to your project → Variables tab and add:

```
SUPABASE_URL=https://zozgvcdnkwtyioyazgmx.supabase.co
SUPABASE_KEY=<your_service_role_key>
MISTRAL_API_KEY=<your_key>
TWILIO_ACCOUNT_SID=AC09c132dca2223eb439efd2ecfa330cb7
TWILIO_AUTH_TOKEN=<your_token>
TWILIO_PHONE_NUMBER=whatsapp:+34625852546
WEBHOOK_API_KEY=prod_dev_secret_key_2025
AGENCY_OWNER_PHONE=+34625852546
AGENCY_OWNER_EMAIL=albertocalvorivas@gmail.com
ENVIRONMENT=production
PORT=8000
```

### 3. Deploy

Railway will automatically:
- Detect `requirements.txt`
- Install Python dependencies
- Use the `Procfile` to start the server
- Expose the application on a public URL

### 4. Get Your Deployment URL

After deployment completes:
1. Go to Settings → Domains
2. Click "Generate Domain"
3. Copy the URL (e.g., `https://agenzia-ai-backend.up.railway.app`)

### 5. Update Frontend Environment

Update `/apps/dashboard/.env.production`:
```bash
VITE_API_URL=https://your-app.up.railway.app
```

### 6. Redeploy Dashboard

```bash
cd apps/dashboard
npm run build:production
vercel --prod --yes
```

## Alternative: Deploy via GitHub Integration

If you prefer automated deployments:

1. Push code to GitHub
2. Connect Railway to your GitHub repo
3. Railway will auto-deploy on every push to main branch

## Verification

Test your deployment:
```bash
# Health check
curl https://your-app.up.railway.app/health

# WebSocket test
wscat -c wss://your-app.up.railway.app/ws/conversations
```
