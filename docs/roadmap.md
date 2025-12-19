# 🚀 Roadmap: From Demo to Production

Now that your system is live on Vercel, here is the technical roadmap to move from a "Live Demo" state to a fully-scaled "Production" operation.

---

## 🛠️ Phase 1: High Priority (Infrastructure)

### 1. Upgrade Twilio to paid account
*   **Why**: Removes the "Sent from Twilio Trial" prefix and the 50 messages/day limit.
*   **Action**: Add $20 credit to your Twilio console and activate a dedicated WhatsApp Business sender.

### 2. Connect Custom Domain
*   **Why**: `agenzia-ai.vercel.app` is great for demos, but `www.agenzia.it` is professional.
*   **Action**: Purchase a domain on Namecheap/GoDaddy and point it to Vercel Settings → Domains.

### 3. Finalize Portal Webhooks
*   **Why**: We've built the endpoints, now they need real data.
*   **Action**: Contact your account manager at Immobiliare.it or Idealista to register your live URL:
    `https://your-domain.com/webhooks/immobiliare`

---

## 🔒 Phase 2: Security & Reliability

### 1. Webhook Authentication (Completed)
*   **Why**: Current webhooks are open. Anyone could spam your API.
*   **Action**: Use the `X-Webhook-Key` header with your secret key. See [Security Guide](api-security.md).

### 2. Move Rate Limiting to Redis
*   **Why**: Current rate limiting is "in-memory". If Vercel restarts, the count resets.
*   **Action**: Use Upstash (Redis for Vercel) to track requests across serverless instances.

### 3. Error Monitoring (Sentry)
*   **Why**: You need to know if the AI fails while you're sleeping.
*   **Action**: Integrate Sentry to get instant alerts on your phone if a webhook returns a 500 error.

---

## 📈 Phase 3: Scaling & Intelligence

### 1. Multi-Agent Team
*   **Concept**: Separate agents for "Inquiry Management" vs "Appointment Reminders".
*   **Action**: Update the prompt logic to handle distinct stages of the funnel.

### 2. PDF Property Cards
*   **Concept**: AI sends a PDF brochure automatically when a client asks for "more details".
*   **Action**: Create a script to generate dynamic PDFs from your Supabase property data.

### 3. Voice Call Mirroring
*   **Concept**: If the client calls the WhatsApp number, they get a Voice AI or your real phone.
*   **Action**: Configure Twilio Studio to forward calls or trigger a Voice AI response.

---

## 📊 Maintenance Checklist (Weekly)

- [ ] **Audit Logs**: Check Supabase `lead_conversations` for AI "misunderstandings".
- [ ] **Update RAG**: Ensure new house listings are added to the properties table via [CSV Import](property-import.md).
- [ ] **Check Sentiment**: Look at the "Takeover Rate" in Analytics to identify where AI needs better prompting.
- [ ] **Invoice Clients**: Cross-reference Google Sheets leads with closed sales.

---

**Next Action Recommended:**  
Upgrade Twilio and connect a custom domain to remove the "Demo" perception from clients. 🚀
