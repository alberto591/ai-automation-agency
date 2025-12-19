# Agenzia AI: Master Execution Guide

This guide provides a comprehensive, step-by-step manual for setting up, running, testing, and maintaining the **Agency CRM & AI Lead Manager**.

---

## 🛠️ 1. Prerequisites & Setup

### Requirements
- **Python 3.10+**
- **Node.js 18+**
- **Supabase Account** (Database & Auth)
- **Mistral AI API Key** (Brain)
- **Twilio Account** (WhatsApp API)

### Initial Installation
1.  **Clone the Repo**:
    ```bash
    git clone https://github.com/alberto591/ai-automation-agency.git
    cd ai-automation-agency
    ```
2.  **Backend Setup**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3.  **Frontend Setup**:
    ```bash
    cd dashboard
    npm install
    ```

---

## ⚙️ 2. Configuration (`.env`)

Create a `.env` file in the root directory and in `dashboard/` (or use `setup_dashboard_env.py`).

| Variable | Description |
| :--- | :--- |
| `SUPABASE_URL` / `KEY` | Connection details for Lead/Property storage. |
| `MISTRAL_API_KEY` | Brain for AI Real Estate profiling. |
| `TWILIO_...` | Account SID, Auth Token, and WhatsApp Number. |
| `WEBHOOK_API_KEY` | Security key for portal lead ingestion. |
| `VITE_API_URL` | Frontend link to Backend (Local: `http://localhost:8000`). |

---

## 🚀 3. Local Execution

### Start Backend (API)
```bash
# In Root
source venv/bin/activate
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### Start Frontend (Dashboard)
```bash
# In /dashboard
npm run dev
```

---

## 🧪 4. Testing & Verification

### Unified Test Suite
Run the following to verify all logic, security, and lead profiling:
```bash
source venv/bin/activate
pytest tests/
```

### Manual Lead Simulation
Test the webhook ingestion manually:
```bash
curl -X POST http://localhost:8000/webhooks/portal \
  -H "X-Webhook-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Lead", "phone": "+39123456789", "source": "manual"}'
```

---

## 🚢 5. Production Deployment

### Backend (Render/Railway/Heroku)
- The system includes a `Procfile` for production.
- Recommended command: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker api:app --bind 0.0.0.0:$PORT`

### Frontend (Vercel/Netlify)
- Root Directory: `dashboard`
- Build Command: `npm run build`
- Output Directory: `dist`
- Routing: Configured via `vercel.json` for SPA support.

---

## 📍 6. Best Practices & Maintenance
- **Logging**: All events are logged via Python `logging`. Check server logs for structured errors.
- **AI Toggle**: Use the Dashboard to switch to `Manual` mode if a lead needs specific human negotiation.
- **Budget Extraction**: The AI automatically handles ranges (e.g., "500k-700k") and stores the maximum value for the CRM.
- **Scalability**: For high traffic, replace the in-memory rate limiter in `api.py` with Redis.

---
*Created by Antigravity AI - Finalized 2025-12-19*
