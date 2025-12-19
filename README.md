# 🏠 Anzevino AI Real Estate Agent

An advanced AI-powered assistant for Italian real estate agencies. Automated lead qualification via WhatsApp, multi-portal integration, and RAG-based property matching.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2F...&env=SUPABASE_URL,SUPABASE_KEY,MISTRAL_API_KEY,TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN,TWILIO_WHATSAPP_NUMBER,WEBHOOK_API_KEY)

## 📖 Documentation
All technical and user guides are centralized in the [**docs/**](docs/README.md) folder:

- [🚀 Production Roadmap](docs/roadmap.md)
- [🔌 Portal Integration](docs/portal-integration.md)
- [🏠 Property CSV Import](docs/property-import.md)
- [🛡️ Security & API](docs/api-security.md)
- [🔄 How it Works (Flow)](docs/customer-flow.md)

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
