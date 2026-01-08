# FiFi AI Launch Action Plan - Week 1

**Created:** 2026-01-08
**Status:** 🚀 READY TO LAUNCH
**Owner:** Sales & Marketing Team
**Review:** Daily standup at 9:00 AM

---

## 🎯 Mission

**Get 3 demo calls booked and 1 pilot signed by end of Week 1 (Jan 14).**

---

## 📊 Current Status Assessment

### ✅ What's DONE (Ready to Launch)

**Product & Technical:**
- ✅ Core product 85% production-ready (WhatsApp AI, Appraisals, Dashboard)
- ✅ 175 unit tests passing (100% critical path coverage)
- ✅ Health check endpoints (`/health`, `/ready`) deployed
- ✅ Monitoring configured (Sentry + Prometheus)
- ✅ Database schema stable with RLS policies
- ✅ Cache layer operational (Redis + fallback)
- ✅ Auth complete with password reset

**Sales & Marketing Materials:**
- ✅ Go-to-market readiness analysis (recommendation: **LAUNCH NOW**)
- ✅ Product positioning document
- ✅ Pricing strategy (€199/€499/Custom, Pilot: €99/€249)
- ✅ Customer explanation guide (10-step framework)
- ✅ Pitch cheat sheet (1-page quick reference)
- ✅ Practice scripts (3 scenarios)
- ✅ Visual pitch deck (6 slides + speaker notes)
- ✅ 30-minute demo script
- ✅ ROI calculator template
- ✅ Documentation organized (marketing/ + sales/ folders)

---

### 🔴 What's BLOCKING (Must Do First)

**Critical - Payment System (TODAY):**
- [ ] Stripe account setup
- [ ] Create payment links (Starter Pilot €99, Professional Pilot €249)
- [ ] Test payment flow end-to-end

**Critical - Booking System (TODAY):**
- [ ] Calendly account setup
- [ ] Create "FiFi AI - Demo Gratuita (30 min)" event
- [ ] Configure availability hours
- [ ] Add custom questions to Calendly

**High Priority - Lead Capture (TODAY):**
- [ ] Typeform/Google Form for pilot signup
- [ ] Link form to payment links
- [ ] Test submission flow

---

### 🟡 What's IN PROGRESS (Nice to Have)

**Infrastructure (Week 2):**
- 🔄 Production Supabase database (can use staging for pilots)
- 🔄 Redis cluster setup (fallback working)
- 🔄 CDN for static assets
- 🔄 Domain + SSL certificates

**Monitoring (Week 2):**
- 🔄 UptimeRobot monitoring `/health`
- 🔄 Production Sentry DSN
- 🔄 Prometheus/Grafana dashboards
- 🔄 Alert rules (Slack/email)

---

## ⚡ IMMEDIATE ACTIONS (Next 48 Hours)

### Today (Jan 8) - Payment & Booking Setup

**Morning (9:00 AM - 12:00 PM):**

#### ☐ Task 1: Stripe Setup (30 min) - **CRITICAL**
1. Go to https://stripe.com/it
2. Sign up with business email
3. Complete business information
4. Add bank account for payouts
5. Verify email
6. **Output:** Stripe dashboard accessible

#### ☐ Task 2: Create Payment Links (15 min)
1. **Starter Pilot Product:**
   - Name: "FiFi AI - Starter Pilot (3 mesi)"
   - Price: €99/month (recurring monthly)
   - Description: "Pilot 3 mesi a €99/mese (poi €199/mese). Include 100 lead/mese, WhatsApp 24/7, valutazioni instant."
   - Create payment link → **Copy URL**

2. **Professional Pilot Product:**
   - Name: "FiFi AI - Professional Pilot (3 mesi)"
   - Price: €249/month (recurring monthly)
   - Description: "Pilot 3 mesi a €249/mese (poi €499/mese). Lead illimitati, supporto priority, AI personalizzato."
   - Create payment link → **Copy URL**

3. **Output:** Save both URLs to `docs/sales/payment-links.txt`

#### ☐ Task 3: Calendly Setup (15 min)
1. Go to calendly.com
2. Create account with business email
3. Create event:
   - Name: "FiFi AI - Demo Gratuita (30 min)"
   - Duration: 30 minutes
   - Location: Google Meet (auto-generated)
   - Availability: Set your working hours
   - Custom questions:
     - Nome agenzia?
     - Quanti lead ricevete al mese?
     - Qual è la vostra sfida più grande con i lead?
4. Copy scheduling link → **Save to `docs/sales/calendly-link.txt`**

---

**Afternoon (2:00 PM - 5:00 PM):**

#### ☐ Task 4: Signup Form (30 min)
**Option A - Typeform (Recommended):**
1. Go to typeform.com, create account
2. Create form: "FiFi AI - Pilot Program"
3. Add questions:
   - Nome e Cognome *
   - Nome Agenzia *
   - Città/Zona *
   - Email *
   - Telefono (WhatsApp) *
   - Numero agenti in agenzia *
   - Quanti lead ricevete al mese? *
   - Quale piano preferisci? (Starter €99 / Professional €249) *
   - Data ideale per iniziare *
4. Add logic jump:
   - If Starter → Show Stripe link (from Task 2)
   - If Professional → Show Stripe link (from Task 2)
5. **Output:** Copy form URL → `docs/sales/signup-form-link.txt`

#### ☐ Task 5: Practice Script (1 hour) - **CRITICAL**
1. Open `docs/sales/20260108_practice-script.md`
2. Record yourself reading Session 1 (cold call) out loud 3x
3. Listen back, count filler words ("um", "uh", "like")
4. Record again, improve
5. **Goal:** < 5 filler words per call

#### ☐ Task 6: Print Cheat Sheet
1. Open `docs/sales/20260108_pitch-cheat-sheet.md`
2. Print 2 copies (one for desk, one for backup)
3. Keep visible during all calls

---

### Tomorrow (Jan 9) - First Outreach

**Morning (9:00 AM - 12:00 PM):**

#### ☐ Task 7: LinkedIn Post #1 (15 min)
Use template from `IMMEDIATE_ACTION.md`:
```
🛌 La tua agenzia dorme. I tuoi lead no.

Scenario tipico:
• 23:00: Cliente scrive "Cerco 2 camere a Milano, budget €300k"
• 09:00: Tu rispondi (era in orario lavorativo...)
• 09:15: Lui risponde "grazie ma ho già trovato"

Questo succede 30 volte al mese?
= €9,000 di commissioni perse

Ho costruito FiFi AI per risolvere questo:
✅ Risponde in 15 secondi, 24/7
✅ Qualifica budget, zona, urgenza automaticamente
✅ Prenota visite mentre dormi

Prime 10 agenzie: 50% sconto × 3 mesi

Demo gratuita → [Calendly Link]

#immobiliare #realestate #AI #automazione #milano
```
**Before posting:** Replace [Calendly Link] with actual link from Task 3

#### ☐ Task 8: Warm Email Outreach (1 hour)
1. Create Google Sheet: "FiFi AI - Lead Tracker"
   - Columns: Date, Contact Name, Agency, Email, Phone, Source, Status, Next Action, Notes
2. List 10 warm contacts (friends, former colleagues, connections)
3. Send email using template from `docs/marketing/20260108_customer-product-explanation-guide.md`
4. **Template:**
```
Subject: [Name], ho lanciato FiFi AI (50% sconto per te)

Ciao [Name],

Ti ricordi quando abbiamo parlato di automazione per le agenzie?

Bene, l'ho costruita e sto cercando le prime 10 agenzie per il pilot.

Cosa fa:
• Risponde ai lead su WhatsApp 24/7 in 15 secondi
• Fa valutazioni immobiliari instant
• Prenota visite automaticamente

ROI tipico: €4,500/mese recuperato (lead notturni persi)

Offerta lancio per te:
€99/mese × 3 mesi (poi €199)
Trial 14 giorni gratis

Vuoi vederlo live? Prenota 15 min qui:
[Calendly Link]

O inizia subito con il trial:
[Signup Form Link]

Fammi sapere!

[Your Name]
[Your Phone - WhatsApp]
```

5. **Goal:** Send to 10 contacts TODAY
6. Update tracker after each email

---

**Afternoon (2:00 PM - 4:00 PM):**

#### ☐ Task 9: Create Lead Tracker (30 min)
Google Sheet with tabs:
- **Leads:** All contacts and their journey stage
- **Demos:** Scheduled demos with prep notes
- **Pilots:** Signed pilots with onboarding dates
- **Metrics:** Weekly dashboard (emails sent, response rate, demos, conversions)

**Template columns for "Leads" tab:**
| Date | Contact Name | Source | Status | Last Touch | Next Action | Notes |
|------|-------------|--------|--------|------------|-------------|-------|

**Status options:**
- CONTACTED (email/DM sent)
- RESPONDED (they replied)
- DEMO_BOOKED (Calendly scheduled)
- DEMO_DONE (demo completed)
- PILOT_SIGNED (payment received)
- CLOSED_LOST (passed)

#### ☐ Task 10: Review Visual Deck (30 min)
1. Open `docs/sales/20260108_visual-pitch-deck.md`
2. Read speaker notes for Slide 2 (Problem) and Slide 4 (ROI)
3. Practice slide transitions out loud
4. Test screen share in Zoom/Google Meet
5. **Goal:** Can present 12-min deck smoothly

---

## 📅 Week 1 Roadmap (Jan 8-14)

### Day 1-2 (Jan 8-9): Setup & First Contact
- ✅ Payment system live (Stripe)
- ✅ Booking system live (Calendly)
- ✅ First LinkedIn post published
- ✅ 10 warm emails sent
- **Goal:** 2-3 responses, 1 demo booked

### Day 3 (Jan 10): Follow-Up Round 1
- ☐ WhatsApp follow-up to email non-responders (Step 7 from IMMEDIATE_ACTION.md)
- ☐ Respond to all inbound questions within 2 hours
- ☐ Send resources to interested leads (demo video, case study, ROI calc)
- **Goal:** 2 demos booked

### Day 4-5 (Jan 11-12): Demo Execution
- ☐ Conduct scheduled demos (use visual deck)
- ☐ Send follow-up emails within 1 hour post-demo
- ☐ Send pilot signup links to interested prospects
- **Goal:** 1 pilot signed

### Day 6-7 (Jan 13-14): Week 1 Review
- ☐ Update lead tracker with all activity
- ☐ Calculate metrics (response rate, demo→pilot conversion)
- ☐ Refine pitch based on objections heard
- ☐ Plan Week 2 outreach (cold outreach expansion)
- **Goal:** 3 demos done, 1 pilot confirmed

---

## 📈 Success Metrics - Week 1

| Metric | Target | How to Track | Status |
|--------|--------|--------------|--------|
| Warm emails sent | 10 | Lead tracker | 🔄 |
| LinkedIn post views | 50+ | LinkedIn analytics | 🔄 |
| Email response rate | 30% | 3/10 responded | 🔄 |
| Demos booked | 3 | Calendly dashboard | 🔄 |
| Demos completed | 2 | Lead tracker | 🔄 |
| Pilots signed | 1 | Stripe dashboard | 🔄 |
| **MRR** | **€99** | 1 pilot × €99 | 🔄 |

**Update this table daily in STATUS.md!**

---

## 🎯 Week 2-4 Roadmap (Preview)

### Week 2 (Jan 15-21): Scale Outreach
- Cold outreach to 20 agencies (LinkedIn scraping + email)
- Create demo video (record live demo, upload to Loom)
- First pilot onboarding session
- **Goal:** 5 demos, 3 pilots signed, €297 MRR

### Week 3 (Jan 22-28): Iteration
- Collect feedback from first 3 pilots
- Fix top 3 pain points
- Refine demo script based on objections
- **Goal:** 5-7 pilots total, testimonial from Pilot #1

### Week 4 (Jan 29-Feb 4): Scale Prep
- First case study published
- Load test with 10 concurrent users
- Open Starter tier to public (no pilot discount)
- **Goal:** 10 pilots, €990 MRR

---

## 🚨 Critical Success Factors

### Must Have (Week 1):
1. ✅ **Cheat sheet printed** and visible during calls
2. ✅ **Calendly link** in email signature, LinkedIn bio
3. ✅ **Lead tracker** updated daily (no lost leads!)
4. ✅ **24-hour response time** to all inbound inquiries
5. ✅ **Practice script** rehearsed 5x before first call

### Nice to Have (Week 2):
- Demo video recorded and uploaded
- LinkedIn profile optimized (banner, headline)
- Email automation (Mailchimp/SendGrid)
- Landing page with embedded Calendly

---

## 🛡️ Risk Mitigation

### Risk 1: No responses to outreach
**Mitigation:**
- Follow up on WhatsApp after 24 hours (personal touch)
- A/B test subject lines (try 2 different versions)
- Offer demo video instead of live call (lower barrier)

### Risk 2: Demos booked but no-shows
**Mitigation:**
- Send calendar invite immediately after booking
- Send reminder 24h before (automated via Calendly)
- Send reminder 1h before via WhatsApp

### Risk 3: Demos done but no pilots signed
**Mitigation:**
- Offer 14-day free trial (no credit card)
- Send ROI calculator post-demo
- Schedule follow-up call with decision maker

### Risk 4: Technical issues during demo
**Mitigation:**
- Test screen share 30 min before each demo
- Have backup plan (slides as PDF if live demo fails)
- Record demos locally for review/improvement

---

## 📋 Daily Standup Checklist

**Every Morning at 9:00 AM:**

1. **Review Lead Tracker:**
   - Any new responses since yesterday?
   - Any demos scheduled for today?
   - Any follow-ups due today?

2. **Update Metrics:**
   - Emails sent (cumulative)
   - Responses received
   - Demos booked
   - Pilots signed
   - MRR

3. **Plan Today's Actions:**
   - Which contacts to follow up with?
   - Any demos to prep for?
   - Any outreach to send?

4. **Blockers:**
   - Anything preventing progress?
   - Need help with anything?

---

## 📞 Quick Reference Links

**Tools:**
- Stripe Dashboard: https://dashboard.stripe.com
- Calendly: https://calendly.com
- Lead Tracker: [Google Sheet URL]
- Typeform: [Signup Form URL]

**Internal Docs:**
- Cheat Sheet: `docs/sales/20260108_pitch-cheat-sheet.md`
- Practice Script: `docs/sales/20260108_practice-script.md`
- Visual Deck: `docs/sales/20260108_visual-pitch-deck.md`
- Demo Script: `docs/sales/demo-script.md`
- IMMEDIATE_ACTION: `docs/sales/IMMEDIATE_ACTION.md`

**External Resources:**
- Payment Links: `docs/sales/payment-links.txt` (create this)
- Calendly Link: `docs/sales/calendly-link.txt` (create this)
- Signup Form: `docs/sales/signup-form-link.txt` (create this)

---

## ✅ TODAY'S ACTION ITEMS (Copy to Task Manager)

**Priority 1 (Must Do TODAY):**
- [ ] Stripe account setup + payment links created
- [ ] Calendly setup + demo event created
- [ ] Typeform/Google Form created
- [ ] Cheat sheet printed
- [ ] Practice script rehearsed 3x

**Priority 2 (Should Do TODAY):**
- [ ] LinkedIn post published
- [ ] 10 warm emails sent
- [ ] Lead tracker created
- [ ] Visual deck reviewed

**Priority 3 (Nice to Have):**
- [ ] Demo video recorded (optional for Week 1)
- [ ] Email signature updated with Calendly link
- [ ] LinkedIn profile optimized

---

## 🎓 Resources & Support

**If you're stuck:**
- Review: `docs/marketing/20260108_go-to-market-readiness.md` (strategic guidance)
- Practice: `docs/sales/20260108_practice-script.md` (rehearsal scenarios)
- Quick lookup: `docs/sales/20260108_pitch-cheat-sheet.md` (during calls)

**For questions:**
- Technical issues: Check `/health` and `/ready` endpoints
- Sales questions: Review `docs/marketing/20260108_customer-product-explanation-guide.md`
- Objections: Section 7 in customer explanation guide

---

## 📊 Weekly Review Template

**End of Week 1 (Jan 14):**

### Achievements:
- Emails sent: ___
- Responses: ___
- Demos booked: ___
- Demos completed: ___
- Pilots signed: ___
- MRR: €___

### Learnings:
- What worked well?
- What didn't work?
- Top objection heard:
- Surprise discovery:

### Adjustments for Week 2:
- Change in pitch:
- Change in targeting:
- Change in follow-up strategy:

---

**Status:** 🚀 READY TO EXECUTE
**Next Update:** Daily at 9:00 AM standup
**Owner:** Sales Team
**Reviewed By:** [Name]
**Date:** 2026-01-08

---

*Let's get the first customer! 🎯*
