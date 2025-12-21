# 10. WhatsApp-First Customer Engagement

* Status: Accepted
* Deciders: Engineering Team, Antigravity Agent
* Date: 2024-01-10 (Retroactive)

## Context and Problem Statement

Traditional real estate workflow involves email chains or phone tag. However, the Italian market is heavily dominant on WhatsApp. We needed to decide on the primary interface for *customers* (not the agents).

## Considered Options

*   **Web Portal**: Users log in to a website to see property matches.
*   **Mobile App**: Users download a dedicated agency app.
*   **WhatsApp Chat Interface**: Users chat natively in their favorite messaging app.

## Decision Outcome

Chosen option: **WhatsApp Chat Interface**.

### Reasoning
1.  **Friction**: Asking a user to download an app or log in to a portal creates huge friction. Everyone already has WhatsApp.
2.  **Open Rates**: WhatsApp open rates (>90%) dwarf email (<20%).
3.  **Speed**: Real estate is fast-moving. Push notifications on WhatsApp are immediate.
4.  **Media**: WhatsApp supports images and location pins natively, perfect for sending property cards.

### User Flow
1.  User clicks a Facebook Ad -> Opens WhatsApp Chat.
2.  AI greets and qualifies (Budget, Zone).
3.  AI sends property images directly in chat.
4.  User requests a visit in chat.

### Positive Consequences
*   Higher lead conversion rates.
*   Zero onboarding for customers.

### Negative Consequences
*   UI constraints (cannot show a map view or complex dashboard inside WhatsApp).
*   Dependency on Meta/Twilio policies.
