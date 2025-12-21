# 6. Twilio for WhatsApp Messaging

* Status: Accepted
* Deciders: Engineering Team, Antigravity Agent
* Date: 2024-01-15 (Retroactive)

## Context and Problem Statement

The primary communication channel for this real estate agent is WhatsApp. We needed a reliable programmatic interface to send and receive WhatsApp messages, handle media (property photos), and manage webhooks for incoming replies.

## Considered Options

*   **WhatsApp Cloud API (Meta Direct)**: Direct integration, lower cost, but more complex setup and strict meta-review policies.
*   **Twilio Programmable Messaging**: Middleware layer, higher cost per message, but significantly better developer experience.
*   **Unofficial APIs**: High risk of banning, unreliable.

## Decision Outcome

Chosen option: **Twilio Programmable Messaging**.

### Reasoning
1.  **Reliability**: Twilio manages the complexity of the underlying WhatsApp infrastructure.
2.  **Sandbox**: The Twilio Sandbox for WhatsApp allows for immediate testing without waiting for Meta Business Verification, enabling rapid prototyping.
3.  **Unified API**: If we decide to add SMS or Voice later, Twilio supports it with the same SDK.
4.  **Python SDK**: Robust and well-documented library (`twilio-python`).

### Positive Consequences
*   Rapid development cycle (started testing in minutes).
*   Detailed logging and debugging tools in the Twilio Console.

### Negative Consequences
*   Higher operational cost per message compared to direct Meta API.
*   Session pricing applies (24-hour windows).
