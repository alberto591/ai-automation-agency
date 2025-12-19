# Agenzia AI: The Autonomous Real Estate Agent 🏠🤖

> **"An entire Real Estate agency in a single Python script."**

Agenzia AI is a full-stack automation system designed to Capture, Qualify, and Convert real estate leads 24/7 using Generative AI (Mistral), WhatsApp (Twilio), and Vector Database (Supabase).

## 🧩 System Architecture: The 5 Pillars

This project is built on **5 Strategic Pillars** that mimic a human agent's workflow:

### 1. CAPTURE (The Ears) 👂
*   **Logic:** Listens for leads via HTTP Webhooks (from Portals like Immobiliare.it/Idealista).
*   **File:** `api.py` (FastAPI Server).
*   **Action:** Parsers the lead name, phone, and specific property interest.

### 2. INTELLIGENCE (The Brain) 🧠
*   **Logic:** Retrieves the *exact* property details from the database (RAG - Retrieval Augmented Generation) to prevent hallucinations.
*   **Data:** Managed via `upload_data.py` -> Supabase.
*   **AI:** Mistral AI generates a hyper-personalized, persuasive pitch based on real data (Price, Amenities, Location).

### 3. ACTION (The Voice) 🗣️
*   **Logic:** Engages the client via WhatsApp.
*   **File:** `lead_manager.py`.
*   **Features:**
    *   Maintains conversation history (Memory).
    *   Handles objections ("Price negotiable?").
    *   Proposes appointment times.

### 4. CONTROL (The Magic Mirror) 👮‍♂️
*   **Logic:** Allows the Human Owner to intervene instantly.
*   **Takeover Mode:** A "Stop" button mutes the AI for a specific client.
*   **Keyword Triggers:** If a client says *"Voglio parlare con un umano"* or *"Trattabile"*, the system **automatically** pauses and alerts the owner.
*   **Alerts:** WhatsApp notifications to the Boss + Email CC of all chats.

### 5. REPORTING (The Dashboard) 📊
*   **Logic:** Tracks every interaction.
*   **Tools:**
    *   **Supabase:** The Source of Truth.
    *   **CSV Export:** `scripts/export_leads.py`.
    *   **No-Code:** Ready for integration with Make.com -> Google Sheets.

---

## 🛠 Tech Stack

*   **Backend:** Python 3.12+, FastAPI
*   **AI Model:** Mistral-Small (via API)
*   **Database:** Supabase (PostgreSQL)
*   **Messaging:** Twilio API (WhatsApp)
*   **Frontend:** HTML5/JS (Landing Page for Lead Capture)
*   **Deploy:** Vercel (Serverless)

---

## 🚀 Quick Start

### 1. Prerequisites
You need accounts for **Supabase**, **Mistral**, and **Twilio**.
Copy `.env.example` to `.env` and fill in your keys.

### 2. Installation
```bash
git clone https://github.com/alberto591/ai-automation-agency.git
cd ai-automation-agency
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run Locally
```bash
# Start the Backend
uvicorn api:app --reload
```

### 4. Run the "Sales Demo"
Want to impress a client? Run the interactive simulation script:
```bash
python demo_live.py
```

---

## 📂 Project Structure

```
├── api.py                  # The Web Server (FastAPI)
├── lead_manager.py         # The Core Logic (AI, Database, Twilio)
├── demo_live.py            # Client Demonstration Script
├── scenario_negotiation.py # Logic Test Script
├── upload_data.py          # Admin Tool: Upload listings to DB
├── scripts/
│   └── export_leads.py     # Admin Tool: Export DB to CSV
└── tests/                  # Unit Tests (Pytest)
```

## 🛡️ Best Practices
*   **Testing:** Run `pytest tests/` to verify logic.
*   **Linting:** Codebase adheres to PEP 8 (checked via `ruff`).
*   **Security:** Environment variables for all API keys.

---
**License:** Private / Commercial Use.
*Built by Antigravity*
