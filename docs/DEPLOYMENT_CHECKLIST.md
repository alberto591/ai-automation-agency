# Deployment Checklist

**Version**: 1.0
**Last Updated**: 2026-01-03
**Purpose**: Ensure safe, reliable deployments of Anzevino AI Real Estate platform

---

## Pre-Deployment Verification

### Code Quality ✅

- [ ] **All linting checks pass**
  ```bash
  ruff check .
  ```
  - Expected: "All checks passed!"

- [ ] **Type checking passes** (optional, non-blocking)
  ```bash
  mypy --strict backend/
  ```
  - Known acceptable warnings: Missing stubs for `redis`, signature mismatches in adapters

- [ ] **Test suite passes** (≥97% pass rate required)
  ```bash
  pytest -v
  ```
  - Target: 147/147 tests passing
  - Minimum acceptable: 143/147 (97%)

### Code Repository ✅

- [ ] **Working tree is clean**
  ```bash
  git status
  ```
  - Expected: "nothing to commit, working tree clean"

- [ ] **Latest changes pushed to master**
  ```bash
  git push origin master
  ```

- [ ] **ADRs created for major changes**
  - Check `docs/adr/` for documentation of architectural decisions

---

## Environment Configuration

### Required Environment Variables 🔐

**Backend API**:
- [ ] `SUPABASE_URL` - Supabase project URL
- [ ] `SUPABASE_KEY` - Anon/public key
- [ ] `SUPABASE_SERVICE_ROLE_KEY` - Service role key (optional, for admin operations)
- [ ] `MISTRAL_API_KEY` - Mistral AI API key
- [ ] `TWILIO_ACCOUNT_SID` - Twilio account identifier
- [ ] `TWILIO_AUTH_TOKEN` - Twilio authentication token
- [ ] `TWILIO_WHATSAPP_NUMBER` - WhatsApp business number
- [ ] `WEBHOOK_API_KEY` - Webhook authentication key
- [ ] `RAPIDAPI_KEY` - RapidAPI key for property data
- [ ] `SENTRY_DSN` - Sentry error tracking (optional)

**Frontend (Vercel/Landing Page)**:
- [ ] `VITE_API_URL` - Backend API endpoint URL

### Secrets Management ✅

- [ ] All secrets stored in Vercel environment variables (not in code)
- [ ] `.env.example` updated with new variable names
- [ ] Production secrets rotated if exposed

---

## Database Readiness

### Schema & Migrations 🗄️

- [ ] **Latest migrations applied**
  ```bash
  # Check Supabase dashboard → Database → Migrations
  ```

- [ ] **RLS policies enabled** on all tables exposed to PostgREST
  - Critical: `properties`, `leads`, `messages`, `semantic_cache`

- [ ] **Indexes optimized** for query performance
  - Check: `properties` table has index on frequently queried columns

### Data Quality ✅

- [ ] **Production property data loaded**
  - Target: ≥200 properties for appraisal accuracy
  - Run: `python scripts/gather_production_data.py` if needed

- [ ] **Test data cleaned** (no dummy/dev data in production)

---

## Frontend Deployment (Vercel)

### Build Verification ✅

- [ ] **Local build succeeds**
  ```bash
  cd apps/landing-page
  npm run build
  ```

- [ ] **No build warnings** (check Vercel deployment logs)

- [ ] **Assets optimized** (images compressed, code minified)

### Vercel Configuration ✅

- [ ] **Auto-deploy from GitHub enabled**
  - Connected to `master` branch

- [ ] **Environment variables configured** in Vercel dashboard

- [ ] **Custom domain configured** (if applicable)

- [ ] **SSL/HTTPS enabled** (auto-provisioned by Vercel)

### UI Testing ✅

- [ ] **Appraisal form functional**
  - Test: http://localhost:5173/appraisal/?lang=it
  - Verify: Address input text visible
  - Verify: Form submission works

- [ ] **Landing page renders correctly**
  - Test: http://localhost:5173/
  - Check: Hero section, features, CTA buttons

- [ ] **Mobile responsive** (test on small screen)

---

## Backend Deployment

### API Server ✅

- [ ] **Health check endpoint responds**
  ```bash
  curl http://localhost:8000/health
  ```

- [ ] **API docs accessible**
  - Visit: http://localhost:8000/docs

- [ ] **CORS configured** for frontend domain

### Integration Tests ✅

- [ ] **Appraisal endpoint works**
  ```bash
  python scripts/live_demo.py
  # Select option 4: Direct Appraisal API
  ```
  - Target response time: <10s
  - Check: Investment metrics calculated
  - Check: Comparables found

- [ ] **WhatsApp webhook responds** (if deployed)

- [ ] **Portal integration active** (if configured)

---

## Post-Deployment Verification

### Smoke Tests 🔥

**Within 5 minutes of deployment**:

- [ ] **Landing page loads** (production URL)
- [ ] **Appraisal form submits** successfully
- [ ] **API returns valid responses** (use live_demo.py against prod)
- [ ] **No console errors** in browser DevTools

### Monitoring ✅

- [ ] **Sentry error tracking active** (if configured)
  - Check: No new errors in last 10 minutes

- [ ] **Vercel deployment logs clean**
  - No build errors or warnings

- [ ] **Response time acceptable**
  - Appraisal API: <10s
  - Landing page: <2s first load

### User Acceptance ✅

- [ ] **Stakeholder demo successful**
  - Use: `python scripts/live_demo.py`
  - Show: Appraisal with investment metrics
  - Verify: UI/UX meets expectations

---

## Rollback Procedure

### If Deployment Fails 🚨

**Immediate Actions**:

1. **Revert to previous deployment** (Vercel):
   ```
   Vercel Dashboard → Deployments → Find last stable → "Promote to Production"
   ```

2. **Check error logs**:
   ```bash
   # Vercel logs
   vercel logs [deployment-url]

   # Sentry dashboard
   https://sentry.io
   ```

3. **Notify stakeholders** of rollback

4. **Create incident report** in `docs/reports/`

### Recovery Checklist ✅

- [ ] Previous stable version promoted
- [ ] Root cause identified
- [ ] Fix implemented in development
- [ ] Fix tested in staging/local
- [ ] Re-deploy when ready

---

## Deployment Cadence

**Recommended Schedule**:
- **Hotfixes**: As needed (breaking bugs, security issues)
- **Features**: Weekly on Fridays (lower traffic)
- **Major releases**: Monthly with stakeholder notification

**Best Practices**:
1. Deploy during low-traffic hours (10 AM - 2 PM CET)
2. Have rollback plan ready
3. Monitor for 30 minutes post-deployment
4. Document changes in CHANGELOG.md (if maintained)

---

## Quick Reference Commands

```bash
# Pre-deployment checks
ruff check . && pytest -v && git status

# Start local servers for testing
cd apps/landing-page && npm run dev  # Port 5173
uvicorn presentation.api.api:app --reload --port 8000

# Run live demo
python scripts/live_demo.py

# Check deployment status
vercel --prod  # If using Vercel CLI

# Gather production data (if needed)
python scripts/gather_production_data.py
```

---

## Deployment History Reference

| Date | Version | Changes | Status | Notes |
|------|---------|---------|--------|-------|
| 2026-01-03 | v0.1.6 | Test fixes, lint cleanup | ✅ Success | 147/147 tests passing |
| 2026-01-02 | v0.1.5 | UI fix, ADRs, data collection | ✅ Success | Address input visibility |
| 2026-01-01 | v0.1.4 | WhatsApp integration | ✅ Success | Interactive messages |

---

## Sign-off

**Deployer**: _________________
**Date**: _________________
**Approval**: _________________ (if required)

---

*This checklist should be updated as the deployment process evolves. Last review: 2026-01-03*
