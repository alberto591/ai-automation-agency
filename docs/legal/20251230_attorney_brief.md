# Attorney Consultation Brief: Supporto Valutativo Preliminare (AI)

**Date**: December 30, 2024
**Confidentiality**: Strictly Confidential / Legal Privilege
**Subject**: Regulatory Compliance Review for AI-Driven Real Estate Appraisal Support

## 1. Executive Summary
Anzevino AI is deploying a "Supporto Valutativo Preliminare" (Preliminary Valuation Support) tool. This module uses an ensemble of Machine Learning (XGBoost) and Large Language Models (LLMs) to provide instant property price ranges to users.

Given the recent adoption of the **EU AI Act** and the sensitivity of real estate data in Italy, we require a legal review of our technical safeguards and a formal opinion on our risk classification.

---

## 2. Technical State of Art (As of Dec 30, 2025)

### 2.1 Renaming and Positioning
The tool has been rebranded from "AI Appraisal" to **"Supporto Valutativo Preliminare"** to emphasize its role as a decision-support aid rather than a professional valuation.

### 2.2 Human-in-the-Loop (Handoff Flow)
To mitigate "Hallucination" and "Algorithmic Bias" risks, we have implemented automated **Human Handoff Triggers**:
- **Uncertainty Trigger**: If the model's confidence interval exceeds 15%, the AI stops and notifies a human agent for review.
- **High-Value Trigger**: Any property estimated above **€2,000,000** is automatically flagged for mandatory human oversight.
- **Sentiment Trigger**: If the user expresses frustration or disputes the estimate, a human agent is notified immediately.

### 2.3 Shadow Mode & Validation (Audit Trail)
We have implemented a **Validation Engine** that:
- Logs every prediction alongside the input features and model version.
- Compares predictions against actual closing prices (Shadow Mode) to detect **Model Drift**.
- Triggers internal alerts if the MAPE (Mean Absolute Percentage Error) exceeds 15%.

---

## 3. Legal Objectives

### 3.1 EU AI Act Classification
**Question**: Does this system qualify as "High-Risk" under Annex III?
- *Our Position*: No. It is a lead-generation and marketing support tool. It is not used for credit scoring (banks), recruitment, or critical infrastructure.
- *Attorney Verification*: We need a formal justification for this classification to include in our compliance documentation.

### 3.2 Professional Liability
**Question**: Is the current "Click-to-Accept" disclaimer and the automated "Preliminary" labeling sufficient to exclude liability for financial loss?
- *Current Disclaimer*: "Accetto che questa è una stima preliminare e non sostituisce un professionista." (IT)

### 3.3 Data Sourcing (OMI & Scrapers)
**Question**: We intend to purchase OMI (Osservatorio del Mercato Immobiliare) data.
- Are there specific clauses needed in our Terms of Service to comply with the license terms of the Agenzia delle Entrate?
- What is the current status of the TDM (Text and Data Mining) exception for scraping public listing portals in Italy?

---

## 4. Specific Requests
1. **Opinion Letter**: Addressing the EU AI Act risk tiering.
2. **Review of Terms of Service**: Specifically the section on AI-generated estimates.
3. **Data Protection Impact Assessment (DPIA)**: Advice on whether the automated processing of addresses/phone numbers for appraisal requires a specific DPIA.

---

**Technical Contact**: AI Development Team / Anzevino AI
**Legal Contact**: [To be assigned]
