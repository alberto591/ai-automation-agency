# Deployment Guide for Agenzia AI

This project is configured for a **Monorepo Deployment** (Frontend + Backend in one repo) on **Vercel**.

## 1. Prerequisites
- [Vercel Account](https://vercel.com/signup)
- [GitHub Account](https://github.com)
- [Supabase Project](https://supabase.com) (Already set up)

## 2. Environment Variables
You will need to add the following secrets to your Vercel Project Settings > Environment Variables:

| Variable | Description | Source |
|---|---|---|
| `VITE_SUPABASE_URL` | Frontend URL | Supabase |
| `VITE_SUPABASE_ANON_KEY` | Frontend Key | Supabase |
| `SUPABASE_URL` | Backend URL | Supabase |
| `SUPABASE_KEY` | Backend Service Key | Supabase |
| `OPENAI_API_KEY` | AI Logic | OpenAI |
| `TWILIO_ACCOUNT_SID` | Voice/SMS | Twilio |
| `TWILIO_AUTH_TOKEN` | Voice/SMS | Twilio |
| `IMAP_PASSWORD` | Email Polling | Gmail App Password |

## 3. Deployment Steps (Vercel)
1.  **Import Project**: Go to Vercel Dashboard -> Add New -> Project -> Import from GitHub.
2.  **Select Repository**: Choose `agenzia-ai`.
3.  **Framework Preset**: Select **Vite**.
4.  **Root Directory**: Leave as `./` (Root).
5.  **Build Command**: `cd dashboard && npm install && npm run build` (This is set in `vercel.json` but correct it if prompted).
6.  **Output Directory**: `dashboard/dist`.
7.  **Deploy**: Click **Deploy**.

## 4. Post-Deployment
-   **Webhooks**: Update your Twilio/Portal webhooks to point to the new Vercel URL (e.g., `https://agenzia-ai.vercel.app/api/webhooks/...`).
-   **CRON Jobs**: For email polling, Vercel supports CRON jobs. Add a `vercel.json` cron entry to call `/api/jobs/poll-emails` (Need to expose the script as an endpoint).

## 5. Troubleshooting
-   **Build Fails**: Check `requirements.txt`.
-   **Auth Fails**: Check `VITE_` variables are exposed to the browser.
