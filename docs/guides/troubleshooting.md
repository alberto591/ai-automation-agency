# Troubleshooting Guide

Common issues and solutions for the Anzevino AI project.

---

## Backend Issues

### API Won't Start

**Error**: `ModuleNotFoundError`
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Error**: `Missing environment variable`
```bash
cp .env.example .env
# Fill in required API keys
```

### Database Connection Failed

**Error**: `Supabase connection error`
- Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Check Supabase dashboard for service status

### Tests Failing

```bash
# Run with verbose output
./venv/bin/pytest tests/unit/test_api.py -v --tb=long

# Check specific test
./venv/bin/pytest tests/unit/test_api.py::test_name -v
```

---

## Frontend Issues

### Build Fails

**Error**: `Cannot find module 'vite'`
```bash
cd apps/<app-name>
rm -rf node_modules
npm install
npm run build
```

### Assets Not Loading (404)

Check Vite `base` configuration:
- Fifi: `base: '/appraisal/'`
- Dashboard: `base: '/dashboard/'`
- Landing: No base (root)

### Port Already in Use

```bash
# Find process
lsof -i :5173

# Kill it
kill -9 <PID>
```

---

## WhatsApp/Twilio Issues

### Webhook Not Receiving Messages

1. Check ngrok is running: `ngrok http 8000`
2. Verify Twilio console webhook URL matches ngrok URL
3. Check ngrok dashboard for incoming requests

### Message Not Sending

- Verify `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`
- Check Twilio console for error logs
- Ensure recipient number format: `+39xxxxxxxxxx`

---

## Vercel Deployment Issues

### Build Failing

```bash
# Test locally first
cd apps/landing-page && npm run build
cd apps/fifi && npm run build
cd apps/dashboard && npm run build
```

### API Routes 404

Check `vercel.json` rewrites configuration.

---

## Git Issues

### Push Rejected

```bash
git pull origin main --rebase
git push origin main
```

### Large File Error

```bash
find . -type f -size +50M
# Add to .gitignore or use Git LFS
```

---

## Quick Diagnostics

```bash
# Check backend health
curl http://localhost:8000/health

# Check Python version
python --version  # Should be 3.11+

# Check Node version
node --version  # Should be 18+

# Verify environment
cat .env | grep -E "^[A-Z]" | head -5
```

---

*See [FIXES_APPLIED.md](FIXES_APPLIED.md) for resolved issues.*
