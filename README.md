# 🏠 Anzevino AI Real Estate Agent

An advanced AI-powered assistant for Italian real estate agencies. Automated lead qualification via WhatsApp, multi-portal integration, RAG-based property matching, and AI-driven property appraisal (Fifi).

## 🎯 Recent Updates (Jan 2026)
- ✅ **Fifi Appraisal UI Fix**: Resolved text visibility issue in address input
- 📚 **RAG & Matching Study**: Comprehensive research for 2026 implementation ([View Study](docs/reference/architecture/2026-01-02_rag-matching-study.md))
- 🧪 **Enhanced Testing**: 138/141 unit tests passing (97.9% coverage)
- 🎬 **Live Demo Tool**: Interactive appraisal testing with investment metrics

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2F...&env=SUPABASE_URL,SUPABASE_KEY,MISTRAL_API_KEY,TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN,TWILIO_WHATSAPP_NUMBER,WEBHOOK_API_KEY)

## 📖 Documentation

### Contributing
- **[Contributing Guidelines](CONTRIBUTING.md)** - Required reading for all contributors
- **[Project Standards](docs/PROJECT_STANDARDS.md)** - Quality standards and enforcement
- **[ADR Policy](docs/README.md)** - Architectural Decision Record requirements

### Guides
All technical and user guides:
- **Deployment Guide**: See [PRODUCTION_DEPLOYMENT.md](docs/PRODUCTION_DEPLOYMENT.md)
- **Live Client Demo**: See [PARTNER_PITCH_DEMO.md](docs/PARTNER_PITCH_DEMO.md) for the live demo script and sales pitch
- **Appraisal Demo**: See [APPRAISAL_DEMO.md](docs/APPRAISAL_DEMO.md) for Fifi appraisal tool testing
- **Developer Guide**: See [master-execution-guide.md](docs/guides/master-execution-guide.md)
- [🏠 Property CSV Import](docs/property-import.md)
- [🛡️ Security & API](docs/api-security.md)
- [🔄 How it Works (Flow)](docs/customer-flow.md)
- [🏛️ Architectural Decision Records (ADRs)](docs/adr/ADR-001-genesis-brain-architecture.md)
- [📚 RAG & Matching Research](docs/reference/architecture/2026-01-02_rag-matching-study.md)
- [📱 Mobile Strategy](docs/adr/ADR-015-mobile-strategy-standardization.md)
- [☁️ Mobile Direct Uploads](docs/adr/ADR-029-mobile-direct-uploads.md)

## 🛠️ Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL + Vector)
- **AI Brain**: Mistral AI (Natural Language + RAG)
- **Messaging**: Twilio (WhatsApp API)
- **Frontend Apps**: `apps/`
  - **Landing Page**: `apps/landing-page` (Marketing)
  - **Dashboard**: `apps/dashboard` (React Admin)
  - **Appraisal Tool (Fifi)**: `apps/fifi` (Lead Magnet)
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
uvicorn presentation.api.api:app --reload --host 0.0.0.0 --port 8000
```

4. **Run Landing Page** (for appraisal UI):
```bash
cd apps/landing-page
npm install
npm run dev
```

5. **Test with Demo Script**:
```bash
python scripts/live_demo.py
# Select scenario 4 for appraisal testing
```

---
*Created with ❤️ for Italian Real Estate Excellence.*
