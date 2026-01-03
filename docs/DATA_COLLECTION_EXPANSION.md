# Data Collection Expansion Plan - Tuscany Focus

**Date Created**: 2026-01-03  
**Purpose**: Expand geographic coverage for demo and production  
**Status**: ⏸️ Awaiting API Quota Renewal

---

## 🎯 Objective

Expand property database from 243 properties (Milano/Firenze/Chianti) to **600-800 properties** with:
1. **Heavy Tuscany coverage** (11 zones) - for demo
2. **Major Italian cities** (Rome, Venice, Naples) - for national reach

---

## 📍 Target Geographic Coverage

### Tuscany (Primary Focus - 420-520 properties)

Demo will be based in Tuscany, so comprehensive coverage is critical.

| City | Zones | Target Properties | Priority |
|------|-------|------------------|----------|
| **Firenze** | Centro, Oltrarno, Campo di Marte | 170 | 🔴 Critical |
| **Siena** | Centro Storico | 60 | 🔴 Critical |
| **Pisa** | Centro, Marina | 90 | 🟡 High |
| **Lucca** | Centro Storico | 50 | 🟡 High |
| **Arezzo** | Centro | 40 | 🟡 High |
| **Grosseto** | Centro | 30 | 🟢 Medium |
| **Livorno** | Centro | 30 | 🟢 Medium |
| **Chianti** | Greve, Castellina | 90 | 🔴 Critical |

**Tuscany Total**: 420-520 properties

---

### Major Cities (National Coverage - 180-280 properties)

| City | Zones | Target Properties | Priority |
|------|-------|------------------|----------|
| **Milano** | Centro, Navigli, Isola | 140 (keep existing) | 🔴 Critical |
| **Roma** | Centro Storico, Trastevere, Parioli | 160 | 🟡 High |
| **Venezia** | San Marco, Cannaregio | 90 | 🟢 Medium |
| **Napoli** | Centro, Vomero | 90 | 🟢 Medium |

**Major Cities Total**: 180-280 properties

---

## 🚧 Current Blocker

### RapidAPI Idealista Quota Exceeded

**Error**:
```
API_FAIL 429: You have exceeded the MONTHLY quota for Requests
```

**Resolution Options**:

1. **Wait for Monthly Reset** (Recommended)
   - Free tier: Renews monthly
   - Cost: $0
   - Timeline: Up to 30 days

2. **Upgrade RapidAPI Plan**
   - Basic Plan: $X/month for Y requests
   - Cost: ~$X/month
   - Timeline: Immediate

3. **Alternative Data Sources**
   - Immobiliare.it API
   - Direct scraping (legal considerations)
   - Manual data entry (time-intensive)

---

## 📊 Expected Impact

### Performance Coverage

**Current** (243 properties):
- Milano: 100% coverage (excellent)
- Firenze: 75% coverage (good)
- Chianti: 70% coverage (good)
- Other cities: 0% coverage

**After Expansion** (600-800 properties):
- **Tuscany**: 90-95% coverage (excellent)
- **Milano**: 100% coverage (excellent)
- **Roma/Venezia/Napoli**: 60-80% coverage (good)
- **Overall local hit rate**: 85-95% (from 80%)

### Cost Savings

At 1,000 appraisals/month with 90% local hit rate:
- **Before expansion**: 80% local → $1.40/month
- **After expansion**: 90% local → **$0.70/month**
- **Annual savings**: $8.40

---

## 🔄 Implementation Plan

### Phase 1: Script Preparation ✅
- [x] Modify `gather_production_data.py` with new ZONES
- [x] Add Tuscany cities (11 zones)
- [x] Add major cities (7 zones)
- [x] Commit changes

### Phase 2: Data Collection ⏸️ (Waiting on API)
- [ ] Wait for API quota renewal OR upgrade plan
- [ ] Run collection for 45-60 minutes
- [ ] Target: 400-600 new properties
- [ ] Monitor deduplication

### Phase 3: Verification ⏭️
- [ ] Analyze new dataset distribution
- [ ] Verify Tuscany coverage >90%
- [ ] Test appraisals in nueva zones
- [ ] Update documentation

---

## 🎯 Demo Preparation

### Tuscany Demo Zones (Priority Order)

1. **Firenze Centro** (60-80 properties)
   - Most popular tourist/investment area
   - High-quality comparables needed

2. **Chianti Wine Region** (50-60 properties)
   - Unique market (villas, farmhouses)
   - Premium pricing

3. **Siena Centro Storico** (40-60 properties)
   - Historic UNESCO site
   - Tourism-driven market

4. **Pisa Centro** (30-40 properties)
   - University town
   - Mixed residential/tourist

5. **Lucca Centro Storico** (30-40 properties)
   - Walled city
   - Boutique property market

---

## 📝 Alternative: Mock Data for Demo

**If API quota remains blocked**, consider:

### Option A: Generate Synthetic Tuscany Data
```python
# Create realistic mock properties based on:
- Existing Firenze/Chianti patterns
- Known Tuscany market prices
- Historical data from other sources
```

**Pros**: Immediate demo capability  
**Cons**: Not real data, less accurate

### Option B: Manual Data Entry
- Manually find 50-100 key Tuscany properties
- Enter via admin interface
- Focus on demo-critical zones

**Pros**: Real data, curated quality  
**Cons**: Time-intensive (~4-6 hours)

---

## 🔧 Workaround Script

**If API is blocked**, alternative collection:

```bash
# Use different API or scraper
python scripts/collect_tuscany_manual.py \
  --source immobiliare \
  --zones "Firenze,Siena,Pisa" \
  --limit 100
```

*(Script to be created if needed)*

---

## ✅ Success Criteria

**Data Quality**:
- [ ] 600-800 total properties
- [ ] >90% Tuscany coverage
- [ ] >50% major cities coverage
- [ ] <5% duplicates
- [ ] >95% complete records (price + sqm)

**Performance**:
- [ ] Local hit rate >90%
- [ ] Tuscany queries <500ms
- [ ] Confidence scores >75%

**Demo Ready**:
- [ ] All Tuscany zones have 30+ properties
- [ ] Firenze Centro has 60+ properties
- [ ] Chianti has 40+ properties
- [ ] Test appraisals successful

---

## 🔍 Next Steps

1. **Check API Quota Status**
   ```bash
   curl https://rapidapi.com/apidojo/api/idealista2/pricing
   ```

2. **If Available**: Run collection
   ```bash
   python scripts/gather_production_data.py --duration 60
   ```

3. **If Blocked**: Choose alternative (synthetic data, manual entry, or different API)

4. **Once Complete**: Verify and test demo scenarios

---

*Status: Awaiting API quota renewal*  
*Last Updated: 2026-01-03*  
*Next Review: When API available or alternative chosen*
