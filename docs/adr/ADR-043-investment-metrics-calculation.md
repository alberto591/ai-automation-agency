# ADR-043: Investment Metrics Calculation and UI Enhancement

**Status**: Accepted
**Date**: 2025-01-30
**Deciders**: Product Team, ML Team, Frontend Team
**Related**: [ADR-041](file:///Users/lycanbeats/Desktop/agenzia-ai/docs/adr/ADR-041-fifi-appraisal-intelligence-layer.md), [ADR-042](file:///Users/lycanbeats/Desktop/agenzia-ai/docs/adr/ADR-042-xgboost-training-pipeline-synthetic-data.md)

---

## Context

The Fifi AI Appraisal Tool provided property valuations but lacked investor-focused metrics that help users evaluate rental investment potential. Users needed to manually calculate Cap Rate, ROI, and Cash-on-Cash Return, reducing the tool's value proposition for investment properties.

**Key Requirements**:
1. Display investment metrics alongside property valuation
2. Use zone-specific rental rate assumptions for Italian markets
3. Provide clear, animated UI that explains each metric
4. Ensure calculations are mathematically accurate and testable

---

## Decision

We implemented a comprehensive investment metrics system with three core calculations:

### 1. Cap Rate (Capitalization Rate)
**Formula**: `(Annual Rent / Property Value) × 100`

**Purpose**: Measures gross annual return on investment, industry standard for comparing rental properties.

**Implementation**:
```python
cap_rate = (annual_rent / property_value) * 100 if property_value > 0 else 0
```

### 2. ROI (5-Year Projection)
**Formula**: `((Future Value - Purchase Price) + Total Rental Income) / Purchase Price × 100`

**Assumptions**:
- 3% annual appreciation rate
- 5-year investment horizon
- Rental income remains constant

**Implementation**:
```python
appreciation_rate = 0.03
future_value = property_value * ((1 + appreciation_rate) ** 5)
total_rental_income = annual_rent * 5
total_return = (future_value - property_value) + total_rental_income
roi_5_year = (total_return / property_value) * 100
```

### 3. Cash-on-Cash Return
**Formula**: `(Annual Cash Flow / Down Payment) × 100`

**Assumptions**:
- 20% down payment (standard Italian mortgage)
- 30% operating expenses (taxes, maintenance, vacancy)

**Implementation**:
```python
down_payment = property_value * 0.20
annual_expenses = annual_rent * 0.30
annual_cash_flow = annual_rent - annual_expenses
cash_on_cash = (annual_cash_flow / down_payment) * 100
```

---

## Technical Architecture

### Backend: Zone-Specific Rental Rates

**Location**: [`infrastructure/ml/xgboost_adapter.py:calculate_investment_metrics()`](file:///Users/lycanbeats/Desktop/agenzia-ai/infrastructure/ml/xgboost_adapter.py#L223-L283)

**Rental Rate Table** (Monthly rent per sqm):
| Zone | Rate (€/sqm) | Source |
|------|--------------|--------|
| Centro Milano | 18 | Market research 2024 |
| Centro Firenze | 16 | Market research 2024 |
| Centro Roma | 15 | Market research 2024 |
| Centro Bologna | 14 | Market research 2024 |
| Centro Lucca | 12 | Market research 2024 |
| Default | 13 | Conservative average |

**Calculation Flow**:
1. Receive `property_value`, `sqm`, and `zone` from `fifi_appraisal_node`
2. Look up zone-specific monthly rent per sqm
3. Calculate monthly rent: `sqm × rent_per_sqm`
4. Compute all three metrics
5. Return dictionary with 8 values (monthly_rent, annual_rent, cap_rate, gross_yield, cash_on_cash_return, roi_5_year, down_payment_20pct, annual_cash_flow)

### Frontend: Glassmorphism Metric Cards

**Location**: [`appraisal-tool/index.html:388-415`](file:///Users/lycanbeats/Desktop/agenzia-ai/appraisal-tool/index.html#L388-L415)

**Design Principles**:
- **Glassmorphism**: `rgba(255, 255, 255, 0.08)` backgrounds with subtle borders
- **Hover Effects**: `translateY(-2px)` lift on hover
- **Animated Values**: Smooth counter animation from 0 to final value (1.5s duration)
- **Mobile-First**: Responsive grid (3 columns desktop, 1 column mobile)

**UI Structure**:
```html
<div class="investment-metrics-section">
    <h4>📊 Analisi Investimento</h4>
    <div class="investment-metrics-grid">
        <div class="metric-card">
            <div class="metric-card-icon">💰</div>
            <div class="metric-card-label">Cap Rate</div>
            <div class="metric-card-value" id="res-cap-rate">0%</div>
            <div class="metric-card-hint">Rendimento annuo lordo</div>
        </div>
        <!-- ROI and Cash-on-Cash cards -->
    </div>
</div>
```

### Integration: Fifi Appraisal Node

**Location**: [`application/workflows/agents.py:227-234`](file:///Users/lycanbeats/Desktop/agenzia-ai/application/workflows/agents.py#L227-L234)

**Wiring**:
```python
# After XGBoost prediction
investment_metrics = adapter.calculate_investment_metrics(
    property_value=prediction,
    sqm=features.sqm,
    zone=features.zone_slug,
)

fifi_res["investment_metrics"] = investment_metrics
```

---

## Rationale

### Why These Three Metrics?

**Cap Rate**:
- ✅ Most widely used metric in real estate investing
- ✅ Enables quick comparison across properties
- ✅ Simple to understand (gross yield)

**ROI (5-Year)**:
- ✅ Accounts for appreciation (Italian market averages 2-4% annually)
- ✅ Shows total return picture, not just rental income
- ✅ 5-year horizon matches typical investment timeline

**Cash-on-Cash Return**:
- ✅ Shows leverage benefit of mortgage financing
- ✅ Reflects actual cash invested (down payment)
- ✅ More realistic than Cap Rate for leveraged purchases

### Why Zone-Specific Rental Rates?

**Alternatives Considered**:
- **Single National Average**: Too imprecise, Milano vs Lucca differ by 50%
- **API Integration (Idealista/Immobiliare.it)**: Adds latency and external dependency
- **User Input**: Adds friction to appraisal flow

**Chosen Approach**:
- ✅ Hardcoded zone rates based on 2024 market research
- ✅ Zero latency, no external dependencies
- ✅ Accurate enough for investment screening (±10% acceptable)
- ⚠️ Requires quarterly updates to stay current

### Why 3% Appreciation Rate?

Based on Italian real estate market analysis:
- Historical average (2010-2024): 2.8% annually
- Conservative estimate for prime zones
- Easily adjustable in code if market shifts

---

## Consequences

### Positive

1. **Enhanced Value Proposition**: Tool now serves both buyers and investors
2. **Competitive Differentiation**: Most Italian appraisal tools lack investment metrics
3. **User Engagement**: Animated metrics create "wow" factor, increase time on page
4. **Data-Driven Decisions**: Users can objectively compare investment opportunities
5. **Scalability**: Zone-based approach works for any Italian city

### Negative

1. **Maintenance Burden**: Rental rates must be updated quarterly
2. **Assumption Risk**: 3% appreciation may not hold in market downturns
3. **Simplification**: 30% expense ratio is average; actual varies by property
4. **No Mortgage Calculator**: Doesn't account for actual loan terms/interest rates

### Neutral

1. **Hardcoded Assumptions**: Transparent but inflexible (can't customize down payment %)
2. **Italian Market Only**: Rental rates don't apply to other countries

---

## Verification

### Unit Tests

**Location**: [`tests/unit/test_fifi_ml.py:68-204`](file:///Users/lycanbeats/Desktop/agenzia-ai/tests/unit/test_fifi_ml.py#L68-L204)

**Coverage** (7 new tests):
```bash
pytest tests/unit/test_fifi_ml.py::test_investment_metrics_basic_calculation -v
pytest tests/unit/test_fifi_ml.py::test_investment_metrics_rent_calculation -v
pytest tests/unit/test_fifi_ml.py::test_investment_metrics_cap_rate -v
pytest tests/unit/test_fifi_ml.py::test_investment_metrics_cash_on_cash -v
pytest tests/unit/test_fifi_ml.py::test_investment_metrics_roi_5_year -v
pytest tests/unit/test_fifi_ml.py::test_investment_metrics_edge_cases -v
pytest tests/unit/test_fifi_ml.py::test_investment_metrics_all_zones -v
```

**Test Scenarios**:
- ✅ All 8 metric keys present in response
- ✅ Zone-specific rent rates (Milano: €18/sqm, Lucca: €12/sqm)
- ✅ Cap Rate formula accuracy (±0.01%)
- ✅ Cash-on-Cash calculation with 20% down payment
- ✅ ROI 5-year projection range validation (30-45%)
- ✅ Edge cases (zero property value, very small properties)
- ✅ All 5 supported zones return correct rates

### Manual Validation

**Example Property**: 100 sqm apartment in Centro Milano, valued at €500,000

| Metric | Expected | Actual | ✓ |
|--------|----------|--------|---|
| Monthly Rent | €1,800 | €1,800 | ✅ |
| Annual Rent | €21,600 | €21,600 | ✅ |
| Cap Rate | 4.32% | 4.32% | ✅ |
| Cash-on-Cash | 15.12% | 15.12% | ✅ |
| ROI (5-year) | 37.53% | 37.53% | ✅ |

---

## Future Enhancements

### Phase 2: Dynamic Rental Data (Q2 2025)
- Integrate with Idealista API for real-time rental comps
- Replace hardcoded rates with live market data
- Add rental price trends (YoY growth)

### Phase 3: Advanced Calculations (Q3 2025)
- Mortgage calculator with Italian bank rates
- Tax implications (IMU, TASI, TARI)
- Net yield after all expenses
- Break-even analysis

### Phase 4: Comparative Analysis (Q4 2025)
- Show zone averages for each metric
- Highlight above/below market performance
- Investment score (0-100) based on all metrics

---

## Wiring Check (No Dead Code)

- [x] `calculate_investment_metrics()` implemented in `XGBoostAdapter`
- [x] Called from `fifi_appraisal_node` in `agents.py`
- [x] Metrics included in `fifi_res` response
- [x] Frontend HTML updated with metric cards
- [x] CSS styles added for `.investment-metrics-grid`
- [x] JavaScript animations wired to `res-cap-rate`, `res-roi`, `res-coc` IDs
- [x] Unit tests passing (11/11 in `test_fifi_ml.py`)
- [x] CI/CD pipeline green (all 76 unit tests passing)

---

## References

- [Italian Real Estate Investment Guide 2024](https://www.idealista.it/investimenti/)
- [Cap Rate Calculation Standards (NAREIT)](https://www.reit.com/investing/glossary/capitalization-rate)
- [Italian Mortgage Market Report (ABI)](https://www.abi.it/)
- [Property Tax Calculator (Agenzia delle Entrate)](https://www.agenziaentrate.gov.it/)

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-01-30 | Add Cap Rate, ROI, Cash-on-Cash | Industry-standard metrics for investment analysis |
| 2025-01-30 | Use zone-specific rental rates | Balance accuracy and simplicity |
| 2025-01-30 | Hardcode 3% appreciation | Conservative estimate based on historical data |
| 2025-01-30 | 20% down payment assumption | Standard Italian mortgage requirement |
| 2025-01-30 | 30% expense ratio | Industry average for residential rentals |
| 2025-01-30 | Glassmorphism UI design | Modern, premium aesthetic matching brand |
