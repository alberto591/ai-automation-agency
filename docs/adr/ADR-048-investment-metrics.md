# ADR-048: Real Estate Investment Metrics for Fifi AI Appraisal

**Status**: Accepted
**Date**: 2025-12-31
**Deciders**: Engineering Team

---

## Context

Fifi AI Appraisal tool provides property valuations but lacked investment analysis capabilities. Real estate investors and agencies need comprehensive financial metrics to evaluate properties beyond just market value.

**Business Need**: Differentiate from competitors by providing investor-grade analysis alongside valuations.

---

## Decision

Implement automatic investment metrics calculation for every appraisal, including:

### Core Metrics
1. **Cap Rate**: `(Annual Net Income / Property Price) × 100`
2. **ROI**: Return on investment percentage
3. **Price-to-Rent Ratio**: Market valuation efficiency
4. **Cash-on-Cash Return**: Leveraged investment returns
5. **Monthly Cash Flow**: Net rental income projections
6. **Breakeven Analysis**: Investment recovery timeline

### Implementation
- **Service**: `InvestmentCalculator` in application layer
- **Auto-Calculation**: Every appraisal automatically includes metrics
- **Rental Estimation**: Zone-based rental yield assumptions (3-5% for Italian market)
- **Confidence Scoring**: Data quality indicators (1-100 scale + 1-5 stars)

---

## Rationale

### Why Auto-Calculate vs Optional?
- **User Experience**: Investors expect this data—don't make them request it
- **Competitive Edge**: Most tools require manual calculation
- **Low Cost**: Computation is trivial once we have property price

### Why Zone-Based Rental Estimates?
- **MVP Speed**: No need to purchase rental data initially
- **Reasonable Accuracy**: Italian market yields are well-documented (3-5%)
- **Refinement Path**: Can integrate actual rental listings later

### Why Confidence Scoring?
- **Transparency**: Users deserve to know data quality
- **Legal Protection**: Reduces liability for low-confidence estimates
- **EU AI Act**: Aligns with transparency requirements

---

## Consequences

### Positive ✅
- **Higher Perceived Value**: Investment metrics justify premium pricing
- **Investor Appeal**: Attracts serious buyers vs casual browsers
- **Data Moat**: More usage = better rental estimates over time
- **Compliance**: Confidence levels support EU AI Act Article 52 disclosure

### Negative ⚠️
- **Estimation Risk**: Rental yields are assumptions, not guarantees
- **Disclaimer Needed**: Must clarify these are estimates, not guarantees
- **Maintenance**: Rental yield assumptions need periodic updates

### Neutral
- **No ML Training**: Uses simple formulas, not machine learning (for now)
- **Backend Only**: Frontend visualization deferred to Phase 2

---

## Technical Details

### InvestmentCalculator Service
```python
def calculate_metrics(
    property_price: int,
    estimated_monthly_rent: int,
    monthly_expenses: int = None,  # Defaults to 30% of rent
    down_payment_pct: float = 20.0,
    interest_rate: float = 4.5
) -> InvestmentMetrics
```

### Rental Estimation Logic
- Premium zones (historic centers): 3% gross yield
- Standard zones: 4% gross yield
- Suburban zones: 5% gross yield

### Confidence Levels
| Comparables | Confidence | Stars |
|-------------|------------|-------|
| 5+          | 90%        | 5     |
| 3-4         | 75%        | 4     |
| 1-2         | 50%        | 3     |
| 0           | 20%        | 1     |

---

## Alternatives Considered

### 1. Manual Calculation by User
**Rejected**: Poor UX, defeats purpose of AI tool

### 2. Integrate with Rental Listing APIs
**Deferred**: Too expensive for MVP (€15k-30k for OMI data)

### 3. ML-Based Rental Prediction
**Deferred**: Need training data first, simple heuristics work for MVP

---

## Migration Path

### Phase 1 (Complete) ✅
- Backend service implementation
- Zone-based rental estimates
- Confidence scoring

### Phase 2 (Future)
- Frontend UI for investment metrics
- Interactive cash flow calculator
- Scenario modeling (What-if analysis)

### Phase 3 (Future)
- Purchase OMI rental data
- ML-based rental prediction model
- Historical ROI tracking

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| User Engagement | 80%+ view investment metrics | Analytics tracking |
| Rental Estimate Accuracy | ±15% of market | User feedback surveys |
| Beta Tester NPS | 8+/10 | Post-pilot survey |

---

## Legal Considerations

### Disclaimers Required
> "Investment metrics are estimates based on market averages. Actual returns may vary. This is not financial advice. Consult a licensed professional before making investment decisions."

### EU AI Act Compliance
- ✅ Confidence levels provide transparency
- ✅ Clear disclosure of AI-generated estimates
- ✅ Human review option available (contact agent)

---

## References

- [Italian Real Estate Yields (2024)](https://www.idealista.it/news/immobiliare/residenziale/2024/01/15/175923-rendimenti-affitti-italia)
- [EU AI Act Article 52](https://artificialintelligenceact.eu/article/52/)
- [Implementation Plan](file:///Users/lycanbeats/.gemini/antigravity/brain/d1bc45f3-6ac9-42c4-b2b4-a0ade0008e6b/implementation_plan.md)
- [Commit `7647ada`](https://github.com/alberto591/ai-automation-agency/commit/7647ada)
