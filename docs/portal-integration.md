# 🔌 Portal Integration Guide

## Your New Webhook Endpoints

| Endpoint | Use Case |
|----------|----------|
| `/webhooks/portal` | Universal (any portal) |
| `/webhooks/immobiliare` | Immobiliare.it specific |
| `/webhooks/email-parser` | Make.com/Zapier email parsing |
| `/webhooks/twilio` | WhatsApp responses |

---

## 🚀 Option 1: Direct Portal Integration

### For Immobiliare.it

**Step 1:** Get your Vercel URL (e.g., `https://agenzia-ai.vercel.app`)

**Step 2:** Register webhook with Immobiliare.it
1. Login to your Immobiliare.it agency dashboard.
2. Go to **Settings** → **Integrations** → **Webhooks**.
3. Add webhook URL: `https://your-app.vercel.app/webhooks/immobiliare`
4. Select events: **New Lead Request**.
5. Save.

**Step 3:** Test
When someone requests info on your property, they'll get an instant WhatsApp message!

---

## 📧 Option 2: Email Parsing with Make.com

If the portal only sends **email notifications**, use this method.

### Step 1: Create Make.com Account
Go to [make.com](https://make.com) and sign up (free tier: 1,000 ops/month).

### Step 2: Create Scenario

**Module 1: Email Trigger**
1. Add module: **Email** → **Watch Emails**.
2. Configure:
   - Connection: Your Gmail/Outlook.
   - Folder: Inbox.
   - Filter: From contains "immobiliare" OR "casa.it".

**Module 2: Text Parser**
1. Add module: **Text Parser** → **Match Pattern**.
2. Pattern for phone number: `(\+39|0)\d{9,10}`.

**Module 3: HTTP Request**
1. Add module: **HTTP** → **Make a Request**.
2. Configure:
   - URL: `https://your-app.vercel.app/webhooks/email-parser`
   - Method: POST
   - Headers: Add `X-Webhook-Key` (See [Security Guide](api-security.md))
   - Body type: JSON
   - Body:
```json
{
  "parsed_name": "{{1.from.name}}",
  "parsed_phone": "{{2.output}}",
  "parsed_email": "{{1.from.email}}",
  "subject": "{{1.subject}}",
  "body": "{{1.text}}",
  "source": "email-immobiliare"
}
```

### Step 3: Activate
Toggle the scenario **ON** and set the schedule to every 1 minute.

---

## 🧪 Test Your Integration

### Test Universal Webhook
```bash
curl -X POST https://your-app.vercel.app/webhooks/portal \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Key: YOUR_SECRET_KEY" \
  -d '{
    "name": "Test Cliente",
    "phone": "+393331234567",
    "property_title": "Villa Milano",
    "source": "manual-test"
  }'
```

---

## ✅ Checklist
- [ ] Deploy to Vercel.
- [ ] Get your webhook URL.
- [ ] Configure `WEBHOOK_API_KEY` in Vercel environment variables.
- [ ] Register webhook with portals or set up Make.com parsing.
- [ ] Verify leads are recorded in Google Sheets/Supabase.
