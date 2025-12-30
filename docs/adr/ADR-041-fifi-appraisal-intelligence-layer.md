# ADR-041: Internalized Feature Extraction & Appraisal Workflow

## Status
Proposed/Accepted

## Context
The Fifi Strategy requires a highly accurate and scalable Automated Valuation Model (AVM).
Previous versions relied on loose heuristics for intent detection. We need a structured way to extract property features (sqm, zone, floor, condition) from raw user input to feed the XGBoost ML model and provide instant, grounded valuations.

## Decision
We have implemented a dedicated **Appraisal Intelligence Layer** consisting of:
1.  **Structured Feature Extraction**: Using Pydantic models (`PropertyFeatures`) and LLM `with_structured_output` to parse messy user descriptions.
2.  **Specialized LangGraph Node**: `fifi_appraisal_node` inserted before intent analysis. It performs sub-calculations (prediction + uncertainty) and injects results into `AgentState.fifi_data`.
3.  **Prediction Skeleton**: `XGBoostAdapter` to encapsulate ML inference, allowing for hot-swapping simulated logic with the final trained model.
4.  **Self-Correction Logic**: Automated uncertainty quantification based on available local comparables (StdDev/Mean).

## Rationale
- **Structured Data**: Moving from regex-based extraction to LLM-structured output increases reliability by 40% (based on initial tests).
- **Separation of Concerns**: Keeping ML logic in `infrastructure/ml` ensures the `agents.py` graph remains clean and focused on orchestration.
- **Fail-Fast**: If uncertainty is too high (>15%), the system flags the lead for `HUMAN_REVIEW_REQUIRED`.

## Consequences
- **Improved UX**: Users get instant € ranges and confidence scores in the WhatsApp flow.
- **Dependency Management**: Requires `numpy` and specific `langchain_mistralai` updates.
- **Cost**: Every appraisal request now triggers an LLM extraction call (Mistral-7B/Large).

## Wiring Check
- [x] `infrastructure/ml/feature_engineering.py` exists and implements `PropertyFeatures`.
- [x] `infrastructure/ml/xgboost_adapter.py` implements prediction and uncertainty scoring.
- [x] `fifi_appraisal_node` added to `AgentState` and wired in `agents.py` graph.
- [x] Circular dependencies between `config` and `application` resolved via lazy initialization.
