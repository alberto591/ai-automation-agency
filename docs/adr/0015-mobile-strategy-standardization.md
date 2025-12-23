# ADR-015: mobile-strategy-standardization (Expo/React Native)

* Status: Accepted
* Deciders: Engineering Team, Antigravity Agent
* Date: 2025-12-21

## Context and Problem Statement

The Anzevino AI agent needs a mobile-first dashboard for real estate agents who are frequently in the field. We need a development path that allows for rapid UI iteration, shared business logic with the web dashboard, and native performance (specifically for push notifications).

## Considered Options

*   **Progressive Web App (PWA)**: Easy to implement, but lacks robust push notification support on iOS and feels less "premium".
*   **Flutter**: Excellent performance, but requires learning Dart and duplicative logic.
*   **React Native (Expo)**: High logic reuse, native performance, and excellent developer experience.

## Decision Outcome

Chosen option: **React Native with Expo**.

### Reasoning
1. **Developer Velocity**: Leverages existing React/JavaScript skills from the web team.
2. **Push Notifications**: Expo's notification service is highly reliable for real-time lead alerts.
3. **Internal Workspace**: Easy to manage as a sibling directory (`/mobile`) to the existing `/dashboard`.

### Positive Consequences
- Unified mental model across web and mobile.
- Accelerated development using Expo Go for immediate testing.

### Negative Consequences
- Slight overhead from the React Native bridge (negligible for this use case).
