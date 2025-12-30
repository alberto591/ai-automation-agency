# 🎯 Lead Qualification Flow: Complete Implementation Guide

**Goal**: Convert casual website visitors into qualified buyers/sellers using a 7-step AI qualification flow.
**Target Market**: Italy (WhatsApp-first approach)

---

## 🚦 Step 1: Lead Classification System

| Lead Type | Score | Normalized (1-10) | Action Strategy | Expected Value |
|-----------|-------|-------------------|-----------------|----------------|
| 🔴 **HOT** | 16-21+ | **9-10** | ⚡️ **Call within 5 min** | €1,000 - €5,000 |
| 🟡 **WARM** | 10-15 | **6-8** | 📧 Email + SMS nurture | €500 - €1,000 |
| 🔵 **COLD** | <10 | **<6** | 🤖 Automated drip campaign | Low / Future |

---

## 🗣️ Step 2: The 7-Question Flow (Italian)

### Q1. INTENT (Right person?)
**"Cerchi di comprare, vendere, o solo informarti?"**
- `[Button]` Comprare (**+3**)
- `[Button]` Vendere (**+2**)
- `[Button]` Affittare (**+1**)
- `[Button]` Solo info (**0**)

### Q2. TIMELINE (Urgency)
**"Quando hai bisogno di una casa?"**
- `[Button]` Entro 30 giorni (**+3**)
- `[Button]` 2-3 mesi (**+2**)
- `[Button]` 6+ mesi (**+1**)
- `[Button]` Non sicuro (**0**)

### Q3. BUDGET (Affordability)
**"Budget massimo in €?"**
- `[Slider]` <€100,000 (**+1**)
- `[Slider]` €100k-300k (**+2**)
- `[Slider]` €300k-600k (**+3**)
- `[Slider]` €600k+ (**+3**)
- `[Button]` "Dipende dall'offerta" (**0**)

### Q4. FINANCING (Readiness)
**"Hai già un'ipoteca approvata?"**
- `[Button]` Sì, pre-approvato (**+3**)
- `[Button]` In processo (**+2**)
- `[Button]` Farò domanda (**+1**)
- `[Button]` Non saprei (**0**)

### Q5. LOCATION (Clarity)
**"Zona preferita? (Firenze, Toscana, Lucca, altro)"**
- `[Input]` Specific neighborhood (**+2**)
- `[Input]` General area (**+1**)
- `[Input]` "Non so" (**0**)

### Q6. PROPERTY TYPE (Specifics)
**"Che tipo di proprietà? (Appartamento, villa, terreno, etc)"**
- `[Input]` Specific type (**+2**)
- `[Input]` "Aperto a opzioni" (**+1**)
- `[Input]` "Non so" (**0**)

### Q7. CONTACT (Engagement)
**"Nome, telefono, email?"**
- `[Input]` Provides all (**+2**)
- `[Input]` Provides partial (**+1**)
- `[Input]` Refuses (**0**)

**MAX SCORE**: 21 Points

---

## 🧮 Step 3: Scoring Algorithm & Logic

```javascript
function calculateLeadScore(lead) {
  let score = 0;

  // Q1: Intent (0-3)
  score += lead.intent === 'buy' ? 3 : lead.intent === 'sell' ? 2 : lead.intent === 'rent' ? 1 : 0;

  // Q2: Timeline (0-3)
  score += lead.timeline === 'urgent' ? 3 : lead.timeline === 'medium' ? 2 : 1;

  // Q3: Budget (0-3)
  score += lead.budget >= 300000 ? 3 : lead.budget >= 100000 ? 2 : 1;

  // Q4: Financing (0-3)
  score += lead.financing === 'approved' ? 3 : lead.financing === 'processing' ? 2 : 1;

  // Q5: Location specificity (0-2)
  score += lead.location_specific ? 2 : 1;

  // Q6: Property type specificity (0-2)
  score += lead.property_specific ? 2 : 1;

  // Q7: Contact info completeness (0-2)
  score += lead.has_phone && lead.has_email ? 2 : 1;

  // Normalize 0-21 to 1-10
  const normalizedScore = Math.min(10, Math.round((score / 21) * 10));

  // Classification
  let type = 'COLD';
  if (normalizedScore >= 9) type = 'HOT';
  else if (normalizedScore >= 6) type = 'WARM';

  return { score: normalizedScore, type };
}
```

---

## 💬 Step 4: Conversational UX (Example)

> **BOT**: "Ciao! 👋 Sono qui per aiutarti a trovare la casa perfetta. Iniziamo?"
>
> **USER**: Clicca [Comprare]
>
> **BOT**: "Ottimo! 🏠 Quando ti serve?"
>
> **USER**: Clicca [Entro 30 giorni]
>
> **BOT**: "Perfetto, acquirente serio 💪. Budget indicativo?"
>
> **USER**: Inserisce €350.000
>
> **BOT**: "Buono! Mutuo già approvato?"
>
> **USER**: Clicca [Sì, pre-approvato]
> *(System Note: Score jumps to HOT range)*
>
> **BOT**: "Fantastico! 🎯 Zona preferita?"
>
> **USER**: "Firenze centro"
>
> **BOT**: "Tipo di immobile?"
>
> **USER**: "Appartamento trilocale"
>
> **BOT**: "Ultimo step per inviarti le proposte: come ti chiami?"
>
> **USER**: "Marco" (+ telefono + email)
>
> **BOT**: "✅ Grazie Marco! Sei un priority match. Uno dei nostri agenti ti contatterà tra 5 minuti con le migliori opportunità."

---

## 🚀 Step 5: Routing & Assignment Strategy

### 1. Priority Routing
- **If Lead = HOT (9-10)**:
  - Assign to Senior Agent immediately
  - Send **SMS Alert** to Agent: "🔴 HOT LEAD: Marco, €350k, Firenze. Call now!"
  - Send **WhatsApp** to Lead: "Ciao Marco, sono Alessandro. Ho visto la tua richiesta. Ti chiamo tra 5 min?"

### 2. Specialist Routing
- `Location == "Firenze"` → Assign to **Florence Specialist**
- `Budget >= €500k` → Assign to **Luxury Specialist**
- `Intent == "Rent"` → Assign to **Rental Team**

### 3. Nurture Routing (Cold/Warm)
- Add to Mailchimp/HubSpot "First-Time Buyer" sequence
- Send automated "Market Report" email
- Re-engage via WhatsApp in 7 days

---

## 🤝 Step 6: Integration with Fifi Appraisal Tool

**The Golden Handoff**:

1. **HOT LEAD**:
   - Show appraisal tool *after* contact capture.
   - "While you wait for our call, check value estimates in your area."
   - Agent uses this data in the first call.

2. **WARM LEAD**:
   - Send appraisal report via email as a "value add".
   - "Here is a free valuation report for your dream area."

3. **COLD LEAD**:
   - Use appraisal tool as a **Lead Magnet**.
   - "Curious about prices? Get a free instant valuation."

---

## ⛔️ Step 7: Disqualification Logic (Red Flags)

Auto-disqualify (Action: "Do Not Contact") if:
1. **Budget < €50,000** (Below service threshold)
2. **Timeline = "Just browsing"** AND **No financing**
3. **No valid contact info** provided
4. Competitor agent already identified
5. Location outside service area (e.g., Sicily)

---

## 📱 Step 8: WhatsApp Strategy (Italy-Specific)

**Why**: 95%+ penetration in Italy vs 15-20% email open rates.

**Agent Alert (Typical)**:
> "🔴 **HOT LEAD ALERT**
> **Name**: Marco Rossi
> **Budget**: €350k
> **Zone**: Firenze
> **Status**: Pre-approved
> **Phone**: +39 333 1234567
> [Click to WhatsApp]"

**Lead Follow-up (Automated)**:
> "Ciao Marco! 👋
> Ho visto che cerchi in zona Firenze per €350k.
> Ho 3 opzioni 'off-market' perfette per te.
> Quando possiamo sentirci?
> - Alessandro, Agenzia XYZ"

---

## 📆 Quick Implementation Plan

**Week 1**:
- [ ] Implement `LeadQualificationNode` in LangGraph
- [ ] Define `LeadScore` schema in database
- [ ] Setup Twilio/WhatsApp templates

**Week 2**:
- [ ] Build Chatbot UI (React/Next.js)
- [ ] Connect CRM (HubSpot/Salesforce)
- [ ] Testing with 50 dummy leads

**Week 3**:
- [ ] Launch Pilot
- [ ] Monitor "Time to First Call" metric
- [ ] Optimize question flow based on drop-offs
