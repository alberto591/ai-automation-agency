# 🎯 Appraisal Demo Guide

Step-by-step guide for demonstrating the Fifi AI Appraisal Tool to stakeholders, partners, and clients.

---

## Overview

The Fifi Appraisal Tool is an AI-powered property valuation system that provides:
- ✅ **Instant Valuations**: AI-driven estimates in seconds
- 📊 **Investment Metrics**: Cap rate, ROI, cash flow projections
- 🏘️ **Market Comparables**: Real-time market data integration
- 📱 **Lead Capture**: Seamless conversion to qualified leads

---

## Demo Setup

### Prerequisites
1. Backend API running (local or production)
2. Landing page running at `http://localhost:5173`
3. Test data ready (see examples below)

### Quick Start
```bash
# Terminal 1: Start backend
cd /path/to/agenzia-ai
source venv/bin/activate
uvicorn presentation.api.api:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start landing page
cd apps/landing-page
npm run dev

# Terminal 3: Demo script (optional)
python scripts/live_demo.py
# Select scenario 4
```

---

## Demo Flow

### 1. Live UI Walkthrough

**Navigate to**: `http://localhost:5173/appraisal/?lang=it`

**Fill in the form with sample data**:

| Field | Example Value | Notes |
|-------|---------------|-------|
| Address | Via Roma 10, Milano | Any Italian address |
| Postcode | 20121 | Milan city center |
| Square Meters | 95 | Typical 2BR apartment |
| Condition | Buono Stato (Good) | Dropdown selection |
| Bedrooms | 2 | Optional |

**Click "Valutação Grátis" (Free Appraisal)**

### 2. Expected Output

The system will display:

```
Estimated Value: €452,500
Value Range: €430,375 - €474,625
Confidence Level: 85% (⭐⭐⭐⭐)
Market Trend: Stable

Investment Metrics:
💰 Cap Rate: 3.6%
📊 ROI: 2.5%
💵 Monthly Cash Flow: €945
📈 Price-to-Rent Ratio: 22.5
⏱️  Breakeven: 40 years
```

### 3. Talking Points

✅ **Speed**: "Notice the instant calculation - no waiting for human appraisers"

✅ **Data-Driven**: "The AI analyzes market data, comparables, and local trends in real-time"

✅ **Investment Focus**: "We don't just tell you the value - we show ROI, cash flow, and investment potential"

✅ **Lead Quality**: "Every appraisal captures contact info and converts browser into qualified lead"

---

## Test Scenarios

### Scenario A: Luxury Property (High Value Trigger)
```json
{
  "city": "Milano",
  "zone": "Centro",
  "surface_sqm": 180,
  "condition": "luxury",
  "bedrooms": 4
}
```
**Expected**: Triggers human review for high-value properties (>€2M)

### Scenario B: Suburban Investment
```json
{
  "city": "Milano",
  "zone": "Periferia",
  "surface_sqm": 75,
  "condition": "good",
  "bedrooms": 2
}
```
**Expected**: Higher cap rate (~5%), better cash flow for investors

### Scenario C: Renovation Opportunity
```json
{
  "city": "Firenze",
  "zone": "Centro Storico",
  "surface_sqm": 110,
  "condition": "poor",
  "bedrooms": 3
}
```
**Expected**: Lower valuation with renovation potential notes

---

## API Demo (Technical Audience)

For technical stakeholders, use the demo script:

```bash
python scripts/live_demo.py
```

**Select Scenario 4**: Direct Appraisal API

This demonstrates:
- Clean JSON request/response
- Investment metrics calculation
- Error handling
- Response timing

**Sample API Request**:
```bash
curl -X POST http:// localhost:8000/api/appraisals/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Milano",
    "zone": "Centro",
    "surface_sqm": 95,
    "condition": "good",
    "bedrooms": 2
  }'
```

---

## Troubleshooting

### Issue: "Text not visible in address field"
✅ **Fixed** (Jan 2026): CSS updated from `var(--slate-800)` to `var(--navy-blue)`

### Issue: "Investment metrics not showing"
- Check that `MISTRAL_API_KEY` is set
- Ensure backend is running
- Verify API endpoint returns `investment_metrics` object

### Issue: "API timeout"
- Check backend logs for errors
- Verify Supabase connection
- Ensure Perplexity API key is valid

---

## Sales Pitch Integration

### For Real Estate Agencies
> "Imagine converting **every website visitor** into a qualified lead. Our AI appraisal tool captures interest, provides instant value, and gives YOU the contact information - automatically."

### For Investors
> "See the **investment potential** instantly - not just the price. Cap rate, cash flow, ROI - all calculated in real-time using market data."

### For PropTech Partners
> "**White-label ready**. Drop this on your site, configure your branding, and start capturing leads in minutes."

---

## Next Steps After Demo

1. ✅ Capture stakeholder feedback
2. 📊 Show dashboard with lead management
3. 📱 Demonstrate WhatsApp integration (if applicable)
4. 📄 Share deployment documentation
5. 🤝 Discuss pricing/partnership options

---

**Demo Assets**:
- UI Screenshots: [See walkthrough](file:///Users/lycanbeats/.gemini/antigravity/brain/5813eb79-42b2-4812-82be-8e8e47daaaaf/walkthrough.md)
- API Documentation: [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)
- Live Demo Script: [live_demo.py](file:///Users/lycanbeats/Desktop/agenzia-ai/scripts/live_demo.py)
