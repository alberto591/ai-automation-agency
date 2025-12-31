# Fifi Integration Guide

**Last Updated**: 2025-12-31

---

## Overview

This guide explains how to connect the Fifi AI Appraisal frontend to the investment metrics backend API.

---

## Current State

### Backend ✅
- **InvestmentCalculator** service (`application/services/investment_calculator.py`)
- **AppraisalService** enhanced with investment metrics
- **API Endpoint**: Already integrated into `/api/leads` response

### Frontend ⚠️
- **UI exists**: Investment metrics display in `apps/fifi/index.html` (lines 206-233)
- **Currently**: Uses simulated data (`script.js` lines 310-318)
- **Needed**: Connect to real backend API

---

## Integration Steps

### Option A: Use Existing Lead API (Current)
The lead creation endpoint already captures appraisal data:

```javascript
// In apps/fifi/script.js, line 286
const payload = {
    name: "AI Appraisal Lead",
    agency: "Fifi Appraisal Tool",
    phone: phone,
    postcode: postcode,
    properties: "RICHIESTA VALUTAZIONE: " + address + " (Condizione: " + condition + ") MQ: " + sqm
};
```

**Enhancement needed**: Backend could calculate metrics and return in response.

### Option B: Create Dedicated Appraisal Endpoint (Recommended)

**1. Create new endpoint** in `presentation/api/api.py`:
```python
@app.post("/api/appraisals/estimate")
async def estimate_property_value(request: AppraisalRequest):
    """Generate property appraisal with investment metrics."""
    service = AppraisalService(research_port=PerplexityResearchAdapter(...))
    result = service.estimate_value(request)
    return result
```

**2. Update frontend** in `scripts.js` (replace lines 293-318):
```javascript
// Call real appraisal API
fetch(`${API_BASE}/api/appraisals/estimate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        city: "Florence",  // Extract from postcode
        zone: postcode,
        surface_sqm: parseInt(sqm),
        condition: condition
    })
})
.then(res => res.json())
.then(appraisal => {
    // Use real data from backend
    const metrics = appraisal.investment_metrics;

    animateValue("res-min", 0, appraisal.estimated_range_min, 1500);
    animateValue("res-max", 0, appraisal.estimated_range_max, 1500);
    animateValue("res-sqm", 0, appraisal.avg_price_sqm, 1500);

    if (metrics) {
        animateValue("res-rent", 0, metrics.monthly_rent || metrics.estimated_rent, 1500);
        animateValue("res-cap-rate", 0, metrics.cap_rate, 1500, true);
        animateValue("res-roi", 0, metrics.roi, 1500, true);
        animateValue("res-coc", 0, metrics.cash_on_cash_return, 1500, true);
    }

    // Update confidence
    document.getElementById('confidence-text').textContent =
        `${appraisal.reliability_stars}★ (${appraisal.confidence_level}%)`;
});
```

---

## Database Migration

**File**: `scripts/migrations/20251230_fifi_avm_foundation.sql`

**Tables Created**:
- `historical_transactions` - Property sales data for training
- `property_features_stats` - Zone-level statistics
- `appraisal_validations` - Performance monitoring

**How to Apply**:
1. Open Supabase Dashboard → SQL Editor
2. Paste contents of migration file
3. Execute

**Note**: Migration creates tables but they start empty. Use mock data generator or OMI data purchase to populate.

---

## Testing

### 1. Test Backend API
```bash
curl -X POST http://localhost:8000/api/appraisals/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Florence",
    "zone": "50100",
    "surface_sqm": 100,
    "condition": "good"
  }'
```

### 2. Test Investment Calculator
```python
from application.services.investment_calculator import InvestmentCalculator

calc = InvestmentCalculator()
metrics = calc.calculate_metrics(
    property_price=300000,
    estimated_monthly_rent=1200
)
print(f"Cap Rate: {metrics.cap_rate}%")
```

### 3. Manual Frontend Test
1. `cd apps/fifi && npm run dev`
2. Fill appraisal form
3. Check browser console for API calls
4. Verify metrics display correctly

---

## Monitoring

**Confidence Levels**: Track in `appraisal_validations` table
**Error Logging**: Check backend logs for calculation errors
**User Feedback**: Monitor WhatsApp responses for accuracy complaints

---

## Next Steps

1. **Immediate**: Run database migration
2. **Short-term**: Create `/api/appraisals/estimate` endpoint
3. **Medium-term**: Purchase OMI data (€15k-30k)
4. **Long-term**: Train ML model on real transactions
