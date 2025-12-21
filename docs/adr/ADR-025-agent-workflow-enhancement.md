# 9. Hybrid Human-AI Handover Protocol

* Status: Accepted
* Deciders: Engineering Team, Antigravity Agent
* Date: 2024-02-20 (Retroactive)

## Context and Problem Statement

AI Agents are not perfect. There are distinct moments in a sales conversation where a human must intervene (e.g., final price negotiation, complex legal questions, or angry clients). The system needs a clear, conflict-free way to pass control between the AI and the Human.

## Considered Options

*   **Auto-Handover**: AI analyses sentiment and decides when to stop.
*   **Co-Pilot**: AI suggests drafts, Human approves every message.
*   **Explicit Toggle**: A binary "AI Auto / Human Mode" switch in the UI.

## Decision Outcome

Chosen option: **Explicit Toggle (with Safety Guardrails)**.

### Reasoning
1.  **Control**: Agents were frustrated when the AI would reply *while* they were typing a response. An explicit "Stop" button (switching to Human Mode) gives them definitive control.
2.  **Clarity**: The UI clearly indicates "AI Active" (Green) or "Human Only" (Grey).
3.  **Safety**: We added a "Resume" button to re-enable the AI later, rather than making it a one-way street.

### Implementation
*   **Database**: `status` column in `lead_conversations` table ('human_mode' vs 'active').
*   **Logic**: Before generating a reply, the `LeadProcessor` checks this status. If 'human_mode', it stays silent and only logs the incoming message.
*   **UI**: Dashboard provided a toggle switch that calls `/api/leads/takeover` and `/api/leads/resume`.

### Positive Consequences
*   Zero "double-speak" (Human and AI talking over each other).
*   Agents feel safer using the tool.
*   Reduced liability on sensitive topics.

### Negative Consequences
*   Requires the human agent to actively monitor the dashboard to "resume" the AI if they forget.
