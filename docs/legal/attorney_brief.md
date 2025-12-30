# Attorney Consultation Brief: Fifi AI Appraisal Tool

**Date**: December 2024
**Confidentiality**: Strictly Confidential
**Product**: Fifi Appraisal (Automated Valuation Model - AVM)

## 1. Executive Summary
"Fifi" is an AI-powered real estate valuation tool designed for the Italian market. It uses machine learning algorithms (XGBoost) trained on historical transaction data and real-time comparable listings to provide property value estimates to homeowners via WhatsApp and a Web Interface.

We are seeking a legal opinion on compliance with:
1.  **EU AI Act (Regulation 2024/1689)**
2.  **Italian Real Estate & Consumer Law**
3.  **GDPR (Data Privacy)**

---

## 2. System Description

### 2.1 Inputs
- **User Provided**: Address, Sqm, Condition, Photos (optional).
- **Automated**: Geospatial data (Proximity to metro, schools), Market trends (Immobiliare.it/Idealista listings).

### 2.2 Processing (The Black Box)
- **Algorithm**: Gradient Boosting Regressor (XGBoost).
- **Training Data**: Historical sales (OMI Agenzia Entrate + Notarial Deeds + Scraped Listings).
- **Logic**: The system calculates a base price per sqm for the micro-zone and applies adjustments based on specific features (floor, elevator, condition).

### 2.3 Outputs
- **Estimated Value Range**: e.g., "€450,000 - €480,000".
- **Confidence Score**: e.g., "High Confidence (85%)".
- **Comparables**: List of 3-5 similar properties sold/listed nearby.
- **Disclaimer**: Standard text stating this is an "estimate" and not a "formal perizia".

---

## 3. Key Legal Questions for Consultation

### 3.1 EU AI Act Classification
- **Question**: Is Fifi considered a **"High-Risk AI System"** under Annex III (Management and operation of critical infrastructure or Essential private services)?
- **Context**: Real estate valuations impact creditworthiness and financial decisions, but Fifi is primarily a lead-generation tool, not a bank-grade underwriting tool.
- **Impact**: If "High-Risk", we need Conformity Assessments, CE Marking, and a Quality Management System.

### 3.2 Professional Liability (Responsabilità Professionale)
- **Question**: To what extent can the agency/developer be held liable if a user relies on a Fifi valuation and sells at a loss?
- **Question**: Is the current disclaimer (see below) sufficient to limit liability under the *Codice del Consumo*?

### 3.3 Data Acquisition & Copyright
- **Question**: Can we legally train our model on public listing data (Immobiliare.it/Idealista) scraped from the web?
- **Context**: The data is publicly visible, but Terms of Service usually prohibit scraping. Does "Text and Data Mining" (TDM) exception apply under EU Copyright Directive?

### 3.4 GDPR & automated Decision Making
- **Question**: Because the valuation is automated, does Article 22 GDPR ("Right not to be subject to a decision based solely on automated processing") apply?
- **Requirement**: Do we need to offer an immediate "Appeal to Human" button?

---

## 4. Proposed Disclaimer (Draft)

> "La stima fornita da Fifi AI è basata su algoritmi automatici e dati di mercato statistici. Non costituisce perizia legale, valutazione professionale o parere vincolante. Il valore reale di mercato può variare in base a condizioni specifiche dell'immobile non rilevabili dall'algoritmo. Anzevino AI declina ogni responsabilità per decisioni finanziarie prese basandosi esclusivamente su questi dati. Si consiglia sempre una valutazione fisica professionale."

---

## 5. Next Steps
We request a formal opinion letter addressing the above points and a fee proposal for drafting the Terms of Service and Privacy Policy specifically for the Fifi AI module.
