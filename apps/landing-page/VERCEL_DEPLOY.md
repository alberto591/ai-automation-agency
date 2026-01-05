# Vercel Deployment Guide

## Quick Deploy (2 minutes)

### Step 1: Install Vercel CLI (if not installed)
```bash
npm install -g vercel
```

### Step 2: Login to Vercel
```bash
vercel login
# Opens browser - login with GitHub/GitLab/Email
```

### Step 3: Deploy!
```bash
cd /Users/lycanbeats/Desktop/agenzia-ai/apps/landing-page
vercel

# Follow prompts:
# ? Set up and deploy? Yes
# ? Which scope? [Your account]
# ? Link to existing project? No
# ? Project name? anzevino-ai-landing (or custom name)
# ? In which directory is your code? ./
# ? Want to override settings? No
```

**First deployment takes ~30 seconds**

✅ You'll get a live URL: `https://your-project.vercel.app`

### Step 4: Production Deploy
```bash
vercel --prod
```

✅ Final URL: `https://your-project.vercel.app` (production)

---

## What Vercel Gives You Automatically

✅ **HTTP/2 & HTTP/3** - Enabled by default
✅ **Global CDN** - 100+ edge locations
✅ **Automatic HTTPS** - Free SSL certs
✅ **Service Workers** - Fully supported
✅ **Gzip & Brotli** - Automatic compression
✅ **Edge Caching** - Static assets cached globally
✅ **Custom Domain** - Free (anzevino.ai)

---

## Vercel Configuration Created

`vercel.json` includes:
- **1-year caching** for `/appraisal/dist/` (minified bundles)
- **No caching** for `sw.js` (service worker updates)
- **Security headers** (XSS, clickjacking protection)

---

## After Deployment

### Add Custom Domain
```bash
# In Vercel dashboard or CLI
vercel domains add anzevino.ai
vercel domains add www.anzevino.ai

# Point DNS:
# A record: @ → Vercel IP (shown in dashboard)
# CNAME: www → cname.vercel-dns.com
```

### Environment Variables (for API)
```bash
# If you need to call your FastAPI backend
vercel env add VITE_API_URL
# Value: https://your-backend.onrender.com
```

### Monitor Performance
- Dashboard: https://vercel.com/dashboard
- Analytics: Automatic (free tier: 100k pageviews/month)
- Web Vitals: Built-in tracking

---

## Deploy from Git (Recommended)

### One-time setup:
1. Push code to GitHub:
   ```bash
   git push origin master
   ```

2. Connect Vercel to GitHub:
   - Go to https://vercel.com/new
   - Import your GitHub repo
   - Auto-detects Vite project
   - Click "Deploy"

3. Auto-deploy on push:
   - Every `git push` → automatic deploy
   - Preview URLs for branches
   - Production on `master` push

---

## Troubleshooting

### Issue: Build fails
**Fix**: Check `package.json` scripts
```json
{
  "scripts": {
    "build": "vite build"
  }
}
```

### Issue: Service worker not working
**Fix**: Verify `vercel.json` headers for `sw.js`

### Issue: 404 on routes
**Fix**: Add to `vercel.json`:
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ]
}
```

---

## Cost

**Free tier includes**:
- Unlimited deployments
- 100GB bandwidth/month
- 100k serverless function invocations
- Custom domain
- Automatic HTTPS
- Analytics (100k pageviews)

**You won't pay anything** unless you exceed limits (very generous for most sites)

---

## Ready to Deploy?

Run these commands:

```bash
cd /Users/lycanbeats/Desktop/agenzia-ai/apps/landing-page
vercel login
vercel
```

That's it! 🚀
