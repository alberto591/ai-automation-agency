# ADR-023: max-tokens-centralization

* Status: Accepted
* Deciders: Engineering Team, Antigravity Agent
* Date: 2024-12-21

## Context and Problem Statement

LLM context windows are finite and costly. Unmanaged history growth in WhatsApp conversations can lead to token overflow or degraded model performance.

## Decision Outcome

Chosen option: **Sliding Window Buffer in `config/settings.py`**.

### Reasoning
1. **Predictability**: Enforcing a strict `MAX_CONTEXT_MESSAGES` (e.g., last 10 interactions) in the `LeadProcessor` ensures we never exceed Mistral's limits.
2. **Performance**: Smaller prompts result in faster inference times.

### Positive Consequences
- Stable operational costs.
- Consistent AI response quality.
- Prevention of context-length errors.
