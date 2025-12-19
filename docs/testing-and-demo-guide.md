# 🧪 Testing & Demo Guide

This guide explains how to use the testing and demonstration tools built for the **AI Real Estate Agent**. These tools allow you to simulate leads, test conversations, and demo the system to partners without needing a live deployment or paid Twilio credits.

---

## 🛡️ 1. Mock Mode (Safe Testing)

**Purpose**: Test the AI logic without spending Twilio credits or hitting daily rate limits.

### Setup
1. Open your `.env` file.
2. Add or set: `MOCK_MODE=True`
3. Restart the API: `Ctrl+C` then `venv/bin/uvicorn api:app --reload`

### How it works
*   The system operates normally, BUT...
*   Instead of sending a real WhatsApp Message, it **logs the message** to a file named `mock_messages.log`.
*   It also prints the message content directly in your terminal in **yellow text**.

---

## 🏆 2. Partner Demo Suite (Automated Show)

**Purpose**: A scripted, 3-scenario performance to impress partners or investors.

### Scenarios Covered
1.  **The Seller**: User requests a free valuation -> AI responds with data.
2.  **The Buyer**: User asks for specific requirements -> AI performs RAG search.
3.  **The Closing**: AI realizes no stock exists -> Pivots to "Sales Pro" mode and alerts you.

### How to Run
```bash
venv/bin/python3 partner_demo_suite.py
```
*Note: Ensure your API is running (`uvicorn api:app ...`) in another terminal.*

---

## 🎮 3. Interactive Relay (Chat with your Terminal)

**Purpose**: Have a full 2-way conversation with the AI using your terminal as the "User Phone". Useful if you don't have `ngrok` or a public IP.

### How to Run
```bash
venv/bin/python3 interactive_demo_relay.py
```

### Instructions
1.  The AI will send a real (or mock) message to your phone.
2.  **Type your reply in the terminal**.
3.  The script sends your reply to the AI, continuing the loop.

---

## 🌐 4. Web Interface Simulator

**Purpose**: A visual, browser-based way to test inbound messages.

### How to use
1.  Ensure the Landing Page server is running: `python3 -m http.server 8080` inside `landing_page/` folder.
2.  Open: [http://localhost:8080/test_interface.html](http://localhost:8080/test_interface.html)
3.  Enter a phone number and message.
4.  Click **"Invia all'AI"**.

The system will process the message as if it came from WhatsApp.

---

## 🔌 5. Direct Simulation Scripts

If you just want to trigger a specific event via command line:

**Simulate Inbound Reply:**
```bash
venv/bin/python3 simulate_reply.py "Vorrei visitare la casa a 200k"
```

**Debug Twilio Connection:**
```bash
venv/bin/python3 debug_twilio.py
```
