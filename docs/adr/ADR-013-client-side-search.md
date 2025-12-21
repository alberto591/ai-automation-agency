# 3. Client-Side Search & Filtering

* Status: Accepted
* Deciders: Engineering Team, Antigravity Agent
* Date: 2025-12-21

## Context and Problem Statement

Users need to quickly find specific conversations in the dashboard sidebar. The leads list is the primary navigation method. We needed to decide where to implement the filtering logic: on the backend (API) or the frontend (Client).

## Considered Options

*   **Server-Side Search**: Sending a query to `/api/leads?search=...` and returning filtered results.
*   **Client-Side Search**: Fetching all active leads and filtering the array in memory.

## Decision Outcome

Chosen option: **Client-Side Search**.

### Reasoning
1.  **Dataset Size**: For a single real estate agency, the number of *active* conversations is typically manageable (< 500). Loading this entirely into memory is trivial for modern browsers.
2.  **Responsiveness**: Client-side filtering offers instant feedback (zero latency) as the user types, without waiting for API roundtrips.
3.  **Simplicity**: It avoids adding complex search endpoints and query parameters to the backend at this stage.

### Positive Consequences
*   **Instant UX**: The search feels snappy and responsive.
*   **Reduced Server Load**: No additional requests are sent while typing.
*   **Simplified Backend**: The API remains focused on CRUD, without needing fuzzy search logic.

### Negative Consequences
*   **Scalability Limit**: If the number of leads grows to thousands, the initial load time and client-side filtering performance will degrade. (Mitigation: Implement pagination/search API when dataset > 1000).
