# ADR-034: Sales Journey Blueprint Implementation

## Status
Accepted

## Context
The AI Agent previously lacked a coherent strategy, reacting passively to user inputs. To match the behavior of a Top-Tier Real Estate Agent, it needs a "Brain" that follows a proven sales script.

## Decision
We implemented a rigid **5-Phase Sales Journey** directly into the LangGraph state machine.

### Phases
1.  **Ingestion/Qualification**: Identify Source (Portal vs Appraisal).
2.  **Hot Lead Activation**: Immediate tagging of Appraisal leads.
3.  **Analysis**: Extraction of `preferences`, `sentiment`, `budget`.
4.  **Steering**: Aggressively moving towards `VISIT` (Appointment).
5.  **Retention/Negotiation**: Using market data to handle objections.

### Consequences
- **State Machine**: The `LeadStatus` enum in the database now strictly maps to these phases (`ACTIVE` -> `HOT` -> `QUALIFIED` -> `APPOINTMENT_REQUESTED`).
- **Prompt Engineering**: System prompts are now "State-Aware", checking `journey_state` to decide whether to answer a question or push for a meeting.

## Alternatives Considered
- **Pure LLM**: Letting the LLM decide when to sell. Rejected because LLMs are too passive/polite without structural forcing functions.
