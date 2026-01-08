# Waliner Deep Dive: Feature Analysis & Implementation Insights

**Date:** 2026-01-08
**Purpose:** Extract learnings from closest competitor for FiFi AI product roadmap
**Status:** Research Complete

---

## Executive Summary

Waliner is the **most similar competitor** to FiFi AI - both target real estate agencies with WhatsApp automation. Their aggressive pricing ($25-100/mo) has captured significant market share, but their **scripted chatbot approach** leaves a clear opportunity for AI-powered solutions.

### Key Takeaways for FiFi AI

1. **We're 4-8x more expensive but 10x smarter** - Justify with AVM + AI
2. **Waliner has features we should adopt** - Especially workflow builder, agent rules, payment reminders
3. **Their CRM integrations are key** - Zoho, Sell.do, Lead Squared (Italian equivalents: Gestim, Getrix)
4. **Broadcast campaigns are table stakes** - We need this for marketing feature parity

---

## Waliner Pricing Analysis

| Plan | Price | Users | Key Differentiators |
|------|-------|-------|---------------------|
| **Standard** | $25/mo (₹2000) | 2 | 500 broadcasts/day, 30 templates |
| **Pro** | $50/mo (₹4167) | 5 | Unlimited broadcasts, scheduled, Chat CRM |
| **Enterprise** | $65-100/mo | Custom | AI-driven NLP, eCommerce integrations |

### Price Comparison with FiFi AI

| Feature | Waliner Standard | Waliner Pro | FiFi Starter | FiFi Pro |
|---------|------------------|-------------|--------------|----------|
| **Price** | $25/mo | $50/mo | €199/mo | €499/mo |
| **AI Type** | Scripted | Scripted | LLM-powered | LLM-powered |
| **Property Valuation** | ❌ | ❌ | ✅ | ✅ |
| **Lead Scoring** | ❌ | ❌ | ✅ | ✅ |
| **Multi-Agent Chat** | ✅ | ✅ | 🔄 Planned | 🔄 Planned |
| **Broadcast Campaigns** | 500/day | Unlimited | ❌ Missing | ❌ Missing |

**Key Insight:** Waliner is 4-8x cheaper, but we offer **true AI + instant valuations**. We need to clearly communicate this value gap.

---

## Feature Deep Dive

### 1. WhatsApp Chat Capabilities

**Waliner Features:**
- Multi-agent live chat (multiple agents on one WhatsApp number)
- Agent rules for chat distribution (assign by tags/expertise)
- Message templates (30 in Standard, more in Pro)
- Interactive chat replies
- Custom greeting messages
- 24/7 automated responses

**FiFi AI Status vs Waliner:**
| Feature | Waliner | FiFi | Priority |
|---------|---------|------|----------|
| Multi-agent chat | ✅ | ⚠️ Dashboard only | HIGH |
| Agent assignment rules | ✅ | ❌ | MEDIUM |
| Message templates | ✅ (30+) | ✅ | ✅ Have |
| Interactive buttons | ✅ | 🔄 Planned | HIGH |
| Custom greetings | ✅ | ✅ | ✅ Have |
| 24/7 automation | ✅ (scripted) | ✅ (AI) | ✅ Better |

**🎯 Features to Adopt:**
1. **Multi-agent chat** - Let agencies assign multiple agents to handle WhatsApp
2. **Agent rules** - Route leads by property type, zone, or agent expertise

---

### 2. Broadcast Campaigns

**Waliner Features:**
- Unlimited campaign broadcasting
- 500/day limit on Standard, unlimited on Pro
- Scheduled broadcasts (up to 2 months ahead)
- Campaign analytics (open rates, engagement)
- Contact segmentation for targeted campaigns

**FiFi AI Status:**
- ❌ **We don't have broadcast campaigns**
- This is a significant feature gap

**🎯 Implementation Recommendation:**

Build a **Campaign Module** that includes:
1. Template-based broadcast messages
2. Audience segmentation (by lead score, zone, property interest)
3. Scheduling up to 1 month ahead
4. Analytics dashboard (sent, delivered, read, replied)
5. Compliance (opt-out handling, rate limiting)

**Effort:** 4-6 weeks
**Impact:** Feature parity, marketing upsell opportunity

---

### 3. Real Estate Specific Workflows

**Waliner has pre-built workflows for:**

| Workflow | Description | FiFi Status |
|----------|-------------|-------------|
| **Lead Capture** | Google/Facebook lead form integration | ❌ Build |
| **Property Details Collection** | Sellers upload photos/videos via WhatsApp | ❌ Build |
| **Site Visit Scheduling** | Automated booking + reminders | ✅ Have |
| **Document Collection** | Request docs, store in CRM | ⚠️ Partial |
| **Payment Reminders** | EMI, rent, maintenance reminders | ❌ Build |
| **Broker Fee Collection** | Payment links in WhatsApp | 🔄 Planned |

**🎯 High-Priority Workflows to Build:**

1. **Lead Form Integration** (Week 1-2)
   - Connect Facebook Lead Ads → FiFi
   - Connect Google Lead Forms → FiFi
   - Auto-send WhatsApp greeting with qualification flow

2. **Payment Reminder Automation** (Week 2-3)
   - Template: "Reminder: €X rent due on [date]"
   - Recurring reminders (monthly, weekly)
   - Stripe payment link integration

3. **Document Collection Flow** (Week 3-4)
   - Request ID, income proof, bank statements
   - Store securely with lead record
   - Status tracking (requested → received → verified)

---

### 4. CRM Integrations

**Waliner Integrates With:**
- **Indian CRMs:** Zoho, Sell.do, Kylas, Lead Squared, Hello Leads, Clevertap
- **E-commerce:** Shopify, WooCommerce, Instamojo, Pabbly
- **Automation:** Zapier, Integromat (Make)

**Italian Equivalents for FiFi AI:**
| Waliner Integration | Italian Equivalent | Priority |
|---------------------|-------------------|----------|
| Zoho CRM | Zoho (available in Italy) | MEDIUM |
| Sell.do | Gestim (Italian RE CRM) | HIGH |
| Lead Squared | Getrix, MIOGEST | HIGH |
| Shopify | N/A (different focus) | LOW |
| Zapier | Zapier/Make | HIGH |

**🎯 Integration Roadmap:**
1. **Zapier/Make** (Q1) - Universal connector
2. **Gestim** (Q2) - Largest Italian RE CRM
3. **Pipedrive** (Q2) - Popular generic CRM in Italy
4. **Getrix/MIOGEST** (Q3) - Secondary Italian CRMs

---

### 5. Analytics & Reporting

**Waliner Analytics:**
- Campaign analytics (broadcasts)
- Customer acquisition tracking
- Contact segmentation insights

**FiFi AI Current State:**
- ✅ Lead scoring dashboard
- ✅ Conversation analytics
- ❌ Campaign broadcast analytics (we don't have campaigns)
- ⚠️ Limited customer acquisition tracking

**🎯 Analytics to Add:**
1. **Source attribution** - Where did lead come from? (Facebook, Google, Portal, Referral)
2. **Funnel conversion rates** - Lead → Qualified → Viewing → Offer → Closed
3. **Agent performance** - Response time, conversion rate, leads handled
4. **ROI calculator** - Show agencies their savings/revenue from FiFi

---

## Feature Adoption Priority Matrix

### Must Have (Q1 2026)

| Feature | Waliner Has | FiFi Status | Effort | Impact |
|---------|-------------|-------------|--------|--------|
| Interactive WhatsApp buttons | ✅ | 🔄 Planned | 2 weeks | HIGH |
| Lead form integrations (FB/Google) | ✅ | ❌ | 3 weeks | HIGH |
| Payment reminder automation | ✅ | ❌ | 2 weeks | HIGH |
| Zapier/Make integration | ✅ | ❌ | 2 weeks | HIGH |

### Should Have (Q2 2026)

| Feature | Waliner Has | FiFi Status | Effort | Impact |
|---------|-------------|-------------|--------|--------|
| Broadcast campaigns | ✅ | ❌ | 4 weeks | MEDIUM |
| Multi-agent chat assignment | ✅ | ❌ | 3 weeks | MEDIUM |
| Agent routing rules | ✅ | ❌ | 2 weeks | MEDIUM |
| Document collection flow | ✅ | ⚠️ Partial | 2 weeks | MEDIUM |

### Nice to Have (Q3 2026)

| Feature | Waliner Has | FiFi Status | Effort | Impact |
|---------|-------------|-------------|--------|--------|
| Scheduled broadcasts | ✅ | ❌ | 1 week | LOW |
| Contact import/export | ✅ | ⚠️ Partial | 1 week | LOW |
| Custom chat widgets | ✅ | ❌ | 2 weeks | LOW |

---

## Competitive Positioning vs Waliner

### Where Waliner Wins:
1. **Price** - 4-8x cheaper ($25-100 vs €199-499)
2. **Broadcast campaigns** - Full marketing suite
3. **CRM integrations** - More out-of-box connectors
4. **Multi-agent features** - Mature team collaboration

### Where FiFi AI Wins:
1. **True AI** - LLM-powered conversations vs scripted flows
2. **Property valuations** - Instant AVM (they don't have)
3. **Lead scoring** - HOT/WARM/COLD intelligence
4. **Italian focus** - Built for Italian market, language, regulations

### Battle Card: FiFi vs Waliner

**When prospect says "Waliner is cheaper":**
> "Yes, Waliner is $50/month and we're €199. Here's the difference: Waliner uses scripted chatbots - fixed question trees. Our AI actually understands context. When a buyer says 'I want a bilocale with terrazzo in Navigli under 400k,' our AI knows what that means. Waliner asks 'What's your budget? What's your preferred location?' one by one.
>
> Plus, we generate instant property valuations in 2 minutes. Waliner doesn't. That alone is worth €50/report to most agencies.
>
> The €6/day difference pays for itself with the first lead you don't lose."

**When prospect says "We need broadcast campaigns":**
> "We're adding broadcast campaigns in Q2 2026. Right now, we focus on what matters most: converting the leads you already have. Most agencies lose 40% of leads to slow response. Fix that first, then scale with broadcasts."

---

## Technical Implementation Notes

### WhatsApp Interactive Buttons (Priority)

Waliner uses WhatsApp's interactive message types:
- **Quick Reply Buttons:** Up to 3 buttons for fast responses
- **List Messages:** Up to 10 options in expandable list
- **Call-to-Action Buttons:** Phone call or website link

**FiFi Implementation:**
```python
# Interactive button message structure
{
    "type": "interactive",
    "interactive": {
        "type": "button",
        "body": {"text": "Interested in this property?"},
        "action": {
            "buttons": [
                {"type": "reply", "reply": {"id": "book_visit", "title": "📅 Book Visit"}},
                {"type": "reply", "reply": {"id": "more_info", "title": "ℹ️ More Info"}},
                {"type": "reply", "reply": {"id": "not_interested", "title": "❌ Not Now"}}
            ]
        }
    }
}
```

### Payment Reminder Flow

Waliner workflow for rent/EMI reminders:
1. Store payment due date with contact
2. Trigger reminder 7 days before
3. Send follow-up 3 days before
4. Send urgent reminder on due date
5. Include Stripe/payment link

**FiFi Database Schema Addition:**
```sql
CREATE TABLE payment_schedules (
    id UUID PRIMARY KEY,
    lead_id UUID REFERENCES leads(id),
    payment_type VARCHAR(50), -- 'rent', 'deposit', 'commission', 'emi'
    amount DECIMAL(10,2),
    due_date DATE,
    recurrence VARCHAR(20), -- 'monthly', 'quarterly', 'one-time'
    reminder_days INT[], -- [7, 3, 0]
    status VARCHAR(20), -- 'pending', 'paid', 'overdue'
    stripe_link TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Action Items

### Immediate (This Week)
- [ ] Add interactive buttons to WhatsApp messages
- [ ] Research Meta's latest interactive message APIs
- [ ] Plan lead form integration (Facebook Lead Ads)

### Short Term (Q1 2026)
- [ ] Implement payment reminder automation
- [ ] Build Zapier/Make integration
- [ ] Add multi-agent chat support

### Medium Term (Q2 2026)
- [ ] Launch broadcast campaign feature
- [ ] Integrate with Gestim CRM
- [ ] Build agent routing rules

---

## Conclusion

Waliner is the **floor** of WhatsApp real estate automation. They've proven the market exists and established feature expectations. FiFi AI is the **ceiling** - bringing true AI and instant valuations that Waliner can't match.

**Our strategy is simple:**
1. **Match their core features** (broadcasts, integrations, multi-agent)
2. **Lead with our advantages** (AI, valuations, Italian focus)
3. **Justify the price gap** (€6/day extra for 10x capability)

The next 90 days should focus on closing the feature gap while amplifying our AI differentiation.

---

*Research completed: 2026-01-08*
*Owner: Product Strategy*
