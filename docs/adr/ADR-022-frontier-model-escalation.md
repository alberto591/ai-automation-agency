# 5. Mistral AI for LLM

* Status: Accepted
* Deciders: Engineering Team, Antigravity Agent
* Date: 2024-01-15 (Retroactive)

## Context and Problem Statement

The core of the "Anzevino AI" agent is its ability to understand Italian natural language, carry out conversations, and generate persuasive sales pitches. We needed an LLM that is fluent in Italian, steerable via system prompts, and cost-effective for high-volume automated messaging.

## Considered Options

*   **OpenAI (GPT-3.5/4)**: The industry standard, but potentially higher cost and variable latency.
*   **Mistral AI (via API)**: European-based, efficient models (Mistral-Small, Mistral-Medium).
*   **Local Hosting (Llama 2/3)**: High infrastructure maintenance and hardware requirements.

## Decision Outcome

Chosen option: **Mistral AI**.

### Reasoning
1.  **Language Proficiency**: Mistral models demonstrate excellent performance in European languages, including Italian.
2.  **Cost/Performance Ratio**: Mistral API offers competitive pricing, making it sustainable for a lead generation bot that may handle thousands of messages.
3.  **Function Calling**: Supports structured outputs and tool use, necessary for extracting lead details (budget, zone).
4.  **European Alignment**: Hosting and data processing within the EU (GDPR compliance alignment).

### Positive Consequences
*   High-quality Italian text generation.
*   Lower latency compared to larger models.

### Negative Consequences
*   Ecosystem tools are slightly less mature than OpenAI's (though rapidly catching up).
