# 🏠 Anzevino AI Real Estate Agent

An advanced AI-powered assistant for Italian real estate agencies. Automated lead qualification via WhatsApp, multi-portal integration, and RAG-based property matching.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2F...&env=SUPABASE_URL,SUPABASE_KEY,MISTRAL_API_KEY,TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN,TWILIO_WHATSAPP_NUMBER,WEBHOOK_API_KEY)

## 📖 Documentation

### Contributing
- **[Contributing Guidelines](CONTRIBUTING.md)** - Required reading for all contributors
- **[Project Standards](docs/PROJECT_STANDARDS.md)** - Quality standards and enforcement
- **[ADR Policy](docs/README.md)** - Architectural Decision Record requirements

### Guides
All technical and user guides- **Deployment Guide**: See [PRODUCTION_DEPLOYMENT.md](file:///Users/lycanbeats/Desktop/agenzia-ai/docs/PRODUCTION_DEPLOYMENT.md)
- **Live Client Demo**: See [PARTNER_PITCH_DEMO.md](file:///Users/lycanbeats/Desktop/agenzia-ai/docs/PARTNER_PITCH_DEMO.md) for the live demo script and sales pitch.
- **Developer Guide**: See [MASTER_EXECUTION_GUIDE.md](file:///Users/lycanbeats/Desktop/agenzia-ai/MASTER_EXECUTION_GUIDE.md)
- [🏠 Property CSV Import](docs/property-import.md)
- [🛡️ Security & API](docs/api-security.md)
- [🔄 How it Works (Flow)](docs/customer-flow.md)
- [🏛️ Architectural Decision Records (ADRs)](docs/adr/ADR-001-genesis-brain-architecture.md)
- [📱 Mobile Strategy](docs/adr/ADR-015-mobile-strategy-standardization.md)
- [☁️ Mobile Direct Uploads](docs/adr/ADR-029-mobile-direct-uploads.md)

## 🛠️ Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL + Vector)
- **AI Brain**: Mistral AI (Natural Language + RAG)
- **Messaging**: Twilio (WhatsApp API)
- **Frontend**: Vanilla HTML/CSS/JS (Bilingual IT/EN)
- **Automation**: Make.com / Zapier

## 🚀 Quick Local Setup

1. **Clone & Install**:
```bash
git clone ...
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Environment**:
Copy `.env.example` to `.env` and fill in your keys.

3. **Run API**:
```bash
uvicorn api:app --reload
```

---
*Created with ❤️ for Italian Real Estate Excellence.*
