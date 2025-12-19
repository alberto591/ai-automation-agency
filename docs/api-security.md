# 🛡️ Webhook Security Guide

The API includes a security layer to prevent unauthorized external systems from sending falsified lead data to your webhooks.

## 🔐 X-Webhook-Key Authentication

All public webhook endpoints are protected by a required `X-Webhook-Key` header.

### Protected Endpoints
- `/webhooks/portal`
- `/webhooks/immobiliare`
- `/webhooks/email-parser`
- `/webhooks/twilio` (verification is optional/soft for Twilio to ensure message delivery)

### Configuration
1. **Local**: Set `WEBHOOK_API_KEY` in your `.env` file.
2. **Production**: Add `WEBHOOK_API_KEY` to your Vercel Project Environment Variables.

### Usage in External Tools (Make.com/Postman)
When calling your API, you **must** include the following header:

| Header Key | Value |
| :--- | :--- |
| `X-Webhook-Key` | Your secret key (from environment variables) |

#### Example (cURL)
```bash
curl -X POST https://your-app.vercel.app/webhooks/portal \
  -H "X-Webhook-Key: your_secret_key" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+393330000000"}'
```

---
> [!CAUTION]
> If the header is missing or incorrect, the API will return a `401 Unauthorized` error.
