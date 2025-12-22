# WhatsApp Twilio Integration: Local Development & Testing

Since you are running locally, Twilio cannot send messages directly to localhost. To test this end-to-end:

1. **Use ngrok**: Run `ngrok http 8000` in your terminal.
2. **Configure Twilio**: Copy the generated HTTPS URL (e.g., `https://c999...ngrok.io`).
3. **Update Webhook**: Go to Twilio Console -> WhatsApp Sandbox Settings -> "When a message comes in" -> Paste `YOUR_NGROK_URL/api/webhooks/twilio`.
4. **Test**: Send a WhatsApp message to your Sandbox number. It should appear in your Dashboard!
