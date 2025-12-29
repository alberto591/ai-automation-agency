# Portal Integration Guide 🏗️

This guide explains how to feed leads from **Idealista**, **Immobiliare.it**, and other portals into Anzevino AI using the generic Webhook Endpoint.

## 1. The Endpoint
**URL**: `https://dashboard-henna-rho-50.vercel.app/api/webhooks/portal`
**Method**: `POST`
**Auth**: Header `X-Webhook-Key: <YOUR_WEBHOOK_API_KEY>`

## 2. JSON Payload Format
Send the following JSON body:

```json
{
  "portal_name": "idealista",        // Required: "idealista", "immobiliare", "casa.it"
  "lead_name": "Mario Rossi",        // Required
  "lead_phone": "+393331234567",     // Required
  "lead_email": "mario@email.com",   // Optional
  "message": "Vorrei visitare...",   // Optional
  "property_ref": "RIF-123",         // Optional
  "listing_price": 250000,           // Optional (Integer)
  "property_url": "https://..."      // Optional
}
```

## 3. Recommended Workflow (Make.com / Zapier)
Since most portals do not offer direct webhooks, use an **Email Parser**:

1.  **Trigger**: New Email matches "Nuova richiesta da Idealista" via Gmail/IMAP.
2.  **Action (Parser)**: Extract:
    *   Name
    *   Phone
    *   Message
    *   Ref Code
3.  **Action (HTTP Request)**:
    *   URL: `https://dashboard-henna-rho-50.vercel.app/api/webhooks/portal`
    *   Method: `POST`
    *   Headers: `X-Webhook-Key: prod_dev_secret_key_2025`
    *   Body Type: `JSON` (Map the extracted fields)

## 4. How it Works
1.  The system receives the webhook.
2.  It creates/updates the Lead in the database.
3.  It initiates the AI Agent logic (e.g. checking intent).
4.  It **Syncs to Google Sheets** automatically.
