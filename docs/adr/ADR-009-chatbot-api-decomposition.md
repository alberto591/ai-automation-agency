# 2. Dashboard Component Architecture

* Status: Accepted
* Deciders: Engineering Team, Antigravity Agent
* Date: 2025-12-21

## Context and Problem Statement

The dashboard required a responsive, interactive UI to manage real-time chats, user profiles, and lead details. A monolithic component approach would lead to unmaintainable code and performance issues (unnecessary re-renders). We needed a modular strategy that separated UI presentation from state management logic.

## Considered Options

*   **Monolithic App.jsx**: All state and UI in one file.
*   **Component-Based with Prop Drilling**: Splitting components but passing state deeply.
*   **Modular Components with Custom Hooks**: Separating logic into `use*` hooks and keeping UI components focused on rendering.

## Decision Outcome

Chosen option: **Modular Components with Custom Hooks**.

### Reasoning
1.  **Separation of Concerns**:
    *   `Sidebar`: Handles navigation, search, and lead list rendering.
    *   `ChatWindow`: Handles message display and input.
    *   `ProfileDropdown`: Manages user settings and logout.
    *   `LeadDrawer`: Displays static details.
2.  **State Logic Encapsulation**:
    *   `useLeads`: Encapsulates Supabase subscription and lead fetching.
    *   `useMessages`: Encapsulates message syncing and optimistic updates.
    *   This allows the UI components to remain "dumb" and focus on display.

### Positive Consequences
*   **Maintainability**: Each component is small (< 300 lines) and focused.
*   **Reusability**: `LeadDrawer` or `ProfileDropdown` can be reused or moved easily.
*   **Performance**: State updates in `useMessages` only re-render the `ChatWindow`, not the whole app.

### Negative Consequences
*   Requires understanding of React Hooks pattern.
