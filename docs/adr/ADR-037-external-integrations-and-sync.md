# ADR 037: External Integrations & Data Synchronization

## Status
Accepted

## Context
As the Agenzia AI system moves towards production use, two critical operational needs emerged:
1.  **Operational Visibility**: Human agents need a real-time, accessible view of leads and their status without querying the database directly or relying solely on the technical dashboard.
2.  **Lead Ingestion**: The system needs to ingest leads generated from external real estate portals (Idealista, Immobiliare.it) to trigger the AI sales journey.

## Decision

### 1. Google Sheets for Operational Visibility
We decided to integrate **Google Sheets** as a "read-only" sink for lead data.
-   **Implementation**: A `GoogleSheetsAdapter` (Infrastructure Layer) that authenticates via Service Account.
-   **Trigger Point**: The `finalize_node` in the LangGraph workflow. This ensures that every completed interaction cycle automatically syncs the latest state (Status, Intent, Message Count) to the sheet.
-   **Key Constraint**: Uses Phone Number as the primary key to perform "Upsert" operations (Update if exists, Append if new).

### 2. Generic Portal Webhook for Ingestion
We decided to implement a **Generic Portal Webhook Endpoint** (`POST /api/webhooks/portal`) rather than specific adapters for each portal's proprietary API (which often don't exist or require partnership access).
-   **Middleware Strategy**: Users are expected to use middleware (Make.com, Zapier) to parse emails from portals and forward structured JSON to this endpoint.
-   **Auth**: Protected by `X-Webhook-Key`.
-   **Flow**: Webhook -> `PortalWebhookRequest` -> `LeadProcessor.process_lead()` -> Database & Graph Start.

### 3. Lazy Loading in Dependency Container
To support these integrations, we refined the `Container` configuration.
-   **Problem**: The `finalize_node` (in `agents.py`) needs access to `container.sheets` to perform the sync. However, `container` initializes `LeadProcessor`, which imports `agents`. This created a circular dependency.
-   **Solution**: Implemented accessors for `sheets` in the `Container` using local imports (Lazy Loading). This allows the graph to access infrastructure adapters at runtime without import-time cycles.

## Consequences

### Positive
-   **Immediate Visibility**: Agents can see "Hot" leads in a spreadsheet instantly.
-   **Extensibility**: The portal webhook schema is generic enough to support any source (Website forms, Facebook Leads, etc.).
-   **Resilience**: Sync failures are logged but do not block the main AI conversational flow.

### Negative
-   **Latency**: Google Sheets API calls add latency if not handled asynchronously. (Mitigation: Currently synchronous but wrapped in try/exc; future optimization should move this to `BackgroundTasks` completely if latency becomes an issue).
-   **Middleware Dependency**: Relying on Make/Zapier adds an external dependency for ingestion.

## Compliance
-   **Data Privacy**: Credentials are managed via Environment Variables (`GOOGLE_SHEETS_CREDENTIALS_JSON`).
-   **Architecture**: Follows Hexagonal Architecture (Adapters in Infrastructure, Ports implicit via Duck Typing/Container wiring).
