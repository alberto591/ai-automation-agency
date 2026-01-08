# ROI Calculator - Sales Tool

**Purpose:** Demonstrate financial value during sales conversations  
**Usage:** Fill in yellow cells with prospect's data

---

## Calculator Template (Import to Google Sheets/Excel)

### INPUTS (Agency Data)

| Metric | Value | Notes |
|--------|-------|-------|
| Night leads per month | [Input] | Leads received 6PM-9AM |
| Current response rate | [Input %] | % of night leads answered next day |
| Lead→Viewing conversion | [Input %] | Industry avg: 10-15% |
| Viewing→Sale conversion | [Input %] | Industry avg: 30-40% |
| Average commission per sale | €[Input] | Typical: €2,000-€5,000 |
| Agent hourly rate | €[Input] | Avg: €40-€60/hour |

---

### CURRENT STATE CALCULATIONS

| Metric | Formula | Example |
|--------|---------|---------|
| **Total night leads/month** | Input | 50 |
| **Currently answered** | Total × Response Rate | 50 × 40% = 20 |
| **Currently LOST** | Total - Answered | 50 - 20 = 30 |
| **Lost viewings** | Lost × Lead→Viewing % | 30 × 10% = 3 |
| **Lost sales** | Lost Viewings × Viewing→Sale % | 3 × 30% = 0.9 |
| **Lost revenue/month** | Lost Sales × Avg Commission | 0.9 × €3,000 = **€2,700** |

---

### WITH FIFI AI CALCULATIONS

| Metric | Formula | Example |
|--------|---------|---------|
| **AI response rate** | 95% (guaranteed) | 95% |
| **Leads answered** | Total × AI Response Rate | 50 × 95% = 47.5 |
| **LOST leads** | Total - Answered | 50 - 47.5 = 2.5 |
| **Recovered viewings** | (47.5 - 20) × 10% | 2.75 viewings |
| **Recovered sales** | Recovered Viewings × 30% | 0.83 sales |
| **Revenue recovered/month** | Recovered Sales × Avg Commission | 0.83 × €3,000 = **€2,475** |

---

### TIME SAVINGS

| Activity | Time Before | Time After | Savings |
|----------|-------------|------------|---------|
| Answering basic questions | 2 hrs/day | 0.5 hrs/day | 1.5 hrs/day |
| Scheduling viewings | 1 hr/day | 0 hrs/day | 1 hr/day |
| Generating appraisals | 3 hrs/week | 0 hrs/week | 3 hrs/week |
| **Total monthly savings** | - | - | **~45 hours** |
| **Labor cost savings** | 45 hrs × €50/hr | - | **€2,250/month** |

---

### ROI SUMMARY

| Item | Amount |
|------|--------|
| **Monthly Revenue Recovered** | €2,475 |
| **Monthly Labor Savings** | €2,250 |
| **Total Monthly Value** | **€4,725** |
| | |
| **FiFi AI Cost (Starter)** | -€199 |
| **FiFi AI Cost (Professional)** | -€499 |
| | |
| **Net Gain (Starter)** | **€4,526** |
| **Net Gain (Professional)** | **€4,226** |
| | |
| **ROI % (Starter)** | **2,274%** |
| **ROI % (Professional)** | **847%** |

---

## PDF One-Pager Template

### Front Page

```
┌────────────────────────────────────────┐
│  FiFi AI - Your ROI Calculation       │
│                                        │
│  Agency: [Name]                        │
│  Prepared: [Date]                      │
└────────────────────────────────────────┘

YOUR CURRENT SITUATION
━━━━━━━━━━━━━━━━━━━━━━
Night leads per month:        50
Lost to slow response:        30 (60%)
Monthly revenue lost:         €2,700

TIME WASTED
━━━━━━━━━━━━━━━━━━━━━━
Manual queries:               15 hrs/month
Appraisals:                   12 hrs/month
Labor cost:                   €1,350/month

WITH FIFI AI
━━━━━━━━━━━━━━━━━━━━━━
Response rate:                95% (24/7)
Revenue recovered:            €2,475/month
Time saved:                   45 hrs/month

INVESTMENT
━━━━━━━━━━━━━━━━━━━━━━
Monthly cost:                 €199 (Starter)
                              €499 (Professional)

YOUR NET GAIN
━━━━━━━━━━━━━━━━━━━━━━
Revenue + Time Savings:       €4,725/month
ROI (Starter):                2,274%
ROI (Professional):           847%

┌────────────────────────────────────────┐
│  Payback Period: 2 days                │
│  Annual Value: €56,700                 │
└────────────────────────────────────────┘
```

---

## Interactive Calculator (Google Sheets Link)

**Template:** [Create shareable Google Sheet]

**Instructions for sales team:**
1. Make a copy for each prospect
2. Fill in their actual data during discovery
3. Show live calculation during demo
4. Export PDF and email after call

---

## Example Scenarios

### Small Agency (20 leads/month)
- Lost revenue: €1,080/month
- Labor savings: €900/month
- **Total value:** €1,980/month
- **ROI on Starter (€199):** 995%

### Medium Agency (80 leads/month)
- Lost revenue: €4,320/month
- Labor savings: €3,600/month
- **Total value:** €7,920/month
- **ROI on Professional (€499):** 1,587%

### Large Agency (200 leads/month)
- Lost revenue: €10,800/month
- Labor savings: €9,000/month
- **Total value:** €19,800/month
- **ROI on Enterprise (€1,499):** 1,320%

---

## Objection Handling with Numbers

### "€499 is too much"
Show: "You're losing €4,725/month. €499 is 10.5% of that value."

### "I don't get that many night leads"
Show: "Even with 20 leads/month, ROI is 995%. Break-even is just 4 leads."

### "I can't afford it right now"
Show: "Payback period is 2 days. After that, it's pure profit every month."

---

## Next Steps
1. Create Google Sheets template
2. Share with sales team
3. Test in 5 demo calls
4. Refine based on feedback
