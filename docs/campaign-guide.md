# 🚀 Agency Outreach: Campaign Guide

This guide explains how to use your new growth tools to acquire B2B clients (Real Estate Agencies).

---

## 🛠️ Step 1: Generate your Lead List
Use the `agency_outreach.py` script to find agencies in any city. 

**Command:**
```bash
python3 agency_outreach.py --city "Milano" --output docs/outreach_milano.csv
```

---

## 📩 Step 2: The Pitch
The script automatically generates a personalized "outreach_message" for each lead. 

**Recommended Message Strategy:**
1. **The Hook**: Mention their physical location or a recent listing.
2. **The Problem**: *"Do you lose leads at 11 PM?"*
3. **The Solution**: *"Our AI qualifies them in 15 seconds on WhatsApp."*
4. **The CTA**: *"Can I send you a 1-minute demo video?"*

---

## 📲 Step 3: Execution (Trial)
1. Open [docs/outreach_milano_v1.csv](outreach_milano_v1.csv).
2. For the first 3-5 leads, send a manual WhatsApp message or an Audio Message (audio often gets higher response rates in real estate).
3. If they show interest, send them to your [Landing Page](http://localhost:8080) to try the "AI Appraisal" tool themselves.

---

## 📊 Step 4: Measuring Success
Monitor your Supabase `lead_conversations` table.
- **Conversion**: How many "Appraisal" leads turned into physical appointments?
- **AI Accuracy**: Use the [Pro Dashboard](http://localhost:5173) to see if the AI answered their technical questions correctly.

---

### 💡 Pro Tip: Competitive Advantage
Before contacting a specific agency, use `market_scraper.py` on one of *their* current listings. 
Example:
```bash
python3 market_scraper.py <URL-OF-THEIR-HOUSE>
```
When you call them, you can say: *"I noticed your apartment in Navigli is priced 10% above the zone average. My AI just flagged it, want to see the report?"*

---
*Good luck with the campaign! 🚀*
