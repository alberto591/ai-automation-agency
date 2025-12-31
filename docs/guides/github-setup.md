# GitHub Setup Instructions

Quick setup guide for the Anzevino AI Real Estate Agent repository.

## Repository Info

- **Repository**: `alberto591/ai-automation-agency`
- **URL**: `https://github.com/alberto591/ai-automation-agency`

## Initial Setup (One-Time)

If not already connected:

```bash
cd /Users/lycanbeats/Desktop/agenzia-ai

# Add remote
git remote add origin git@github.com:alberto591/ai-automation-agency.git

# Verify
git remote -v
```

## Daily Workflow

```bash
# Pull latest changes
git pull origin main

# Make changes, then stage and commit
git add .
git commit -m "feat: description of changes"

# Push to GitHub
git push origin main
```

## Vercel Integration

This project auto-deploys via Vercel when pushing to `main`:

1. Push triggers GitHub webhook
2. Vercel builds all frontend apps (`apps/landing-page`, `apps/dashboard`, `apps/fifi`)
3. Backend API served via Vercel Functions

## Repository Topics

Recommended GitHub topics:
- `ai-agent`
- `real-estate`
- `whatsapp-automation`
- `fastapi`
- `mistral-ai`
- `langgraph`
- `supabase`

## Collaboration

To invite collaborators:
1. Settings → Collaborators
2. Add collaborator by GitHub username

---

*See [GITHUB_PUSH_GUIDE.md](GITHUB_PUSH_GUIDE.md) for detailed push workflow.*
