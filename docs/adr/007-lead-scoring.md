# 7. Lead Scoring (Keyword Heuristics)

* Status: Accepted
* Deciders: Engineering Team, Antigravity Agent
* Date: 2024-02-01 (Retroactive)

## Context and Problem Statement

Real estate agents receive hundreds of inquiries, but only a fraction are "hot" leads ready to buy. We needed an automated way to prioritize these leads in the dashboard so agents can focus their time efficiently. The challenge was to define "intent" without having a massive historical dataset to train a machine learning model.

## Considered Options

*   **Machine Learning (Black Box)**: Train a classifier on external datasets.
*   **Keyword Heuristics (Deterministic)**: Rule-based points system based on specific keywords.
*   **Manual Tagging**: Asking the human agent to tag leads (too slow).

## Decision Outcome

Chosen option: **Keyword Heuristics (Deterministic)**.

### Reasoning
1.  **Transparency**: Real estate agents need to trust the system. If a lead is marked "Hot", they want to know why. A heuristic model allows us to explain: "Score +20 because they said 'budget' and 'visit'".
2.  **Cold Start**: We didn't have thousands of labeled chats to train a custom ML model initially.
3.  **Tunability**: If we find that the word "mutuo" (mortgage) implies high intent, we can instantly increase its weight in `lead_scoring.py` without retraining.

### Implementation Logic
*   **Base Score**: 0
*   **High Value Keywords (+15)**: "budget", "contanti" (cash), "visita" (visit).
*   **Medium Value Keywords (+5)**: "zona" (zone), "camere" (rooms).
*   **Penalty (-10)**: "affitto" (rent) - if the agency only does sales.

### Positive Consequences
*   Immediate value from day one.
*   Easy to debug and adjust.

### Negative Consequences
*   Nuance lost (e.g., "I have no budget" might trigger the "budget" keyword positive score if not carefully regexed).
*   Requires manual maintenance of keyword lists.
