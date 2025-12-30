# ADR-040: Fifi AVM Development and Testing Protocol

**Status:** Proposed
**Date:** 2024-12-30
**Author:** Anzevino AI Team

## 1. Context (The "Why")
As we transition "Fifi" from a simple lead-magnet to a production-grade Automated Valuation Model (AVM), we need a standardized protocol for developing, deploying, and validating machine learning models. The current heuristic-based "Expert Data" is insufficient for precise valuations in high-stakes transactions.

## 2. Decision
We will implement a rigorous **Model Development Lifecycle (MDLC)** and a **Backtesting Framework** specifically for the Fifi AVM.

### 2.1 Development Strategy
- **Engine**: We adopt **XGBoost (Extreme Gradient Boosting)** as the primary regressor for its ability to handle sparse categorical data (cadastral zones, condition tiers) and mixed feature types.
- **Feature Engineering**:
    - **Primary**: Micro-zone OMI code, Property surface (sqm), Floor level, Elevator presence.
    - **Categorical**: Property condition (5-tier classifier), Energy class.
    - **External**: Distance to nearest Public Transit (GTFS integration).
- **Ground Truth**: Training will be grounded in verified Notarial Deeds (Atto di Vendita) to capture actual transacted prices, rather than optimistic listing prices.

### 2.2 Testing & Validation Strategy
- **Unit Testing**: Strict schema validation for all inputs via Pydantic models.
- **Offline Backtesting**: A dedicated `BacktestEngine` will evaluate model error (MAE/MAPE) against a hold-out dataset of transacted deeds not seen during training.
- **Stability Monitoring**: The system must log a "Confidence Score" (prediction interval) for every valuation.
- **A/B/C Testing**: Routing leads between the Heuristic model, the ML model, and an LLM-grounded expert analysis to measure conversion and accuracy.

## 3. Rationale (The "Proof")
- **XGBoost** provides the best trade-off between performance and interpretability (via SHAP values), which is crucial for legal transparency under the EU AI Act.
- **Deed-based Training** eliminates the "Scraping Bias" where asking prices are inflated compared to final sale prices (typically 5-10% gap in Italy).

## 4. Consequences
- **Positive**: Increased valuation accuracy, higher trust for "Premium" leads, automated report generation.
- **Negative/Trade-offs**: Higher infrastructure cost (model serving), dependency on fresh OMI/Deed data feeds.

## 5. Wiring Check (No Dead Code)
- [ ] `ValuationPort` updated to include `get_ml_valuation`
- [ ] `XGBoostAdapter` stubbed in `infrastructure/ml/`
- [ ] Environment variables for model paths added to `.config/`
- [ ] Logic integrated into `application/workflows/agents.py`
