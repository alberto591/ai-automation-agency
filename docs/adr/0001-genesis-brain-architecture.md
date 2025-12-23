# ADR-001: chatbot-api-decomposition

* Status: Accepted
* Deciders: Engineering Team, Antigravity Agent
* Date: 2025-12-21

## Context and Problem Statement

The codebase was originally structured as a flat collection of scripts (`app.py`, `utils.py`, `db.py`) mixed with various service modules. This led to:
1.  **High Coupling**: Business logic was tightly coupled with infrastructure (e.g., direct SQL queries in API routes).
2.  **Low Testability**: It was difficult to mock dependencies for unit testing.
3.  **Violation of SOLID Principles**: Classes had multiple responsibilities.

We needed a structure that would enforce separation of concerns and allow for easier maintenance and testing, aligning with GEMINI Engineering Standards.

## Considered Options

* **Layered Architecture (Traditional)**: Controller -> Service -> DAO -> DB.
* **Hexagonal Architecture (Ports and Adapters)**: Domain centric, with dependency injection.
* **Microservices**: Splitting into separate deployable units.

## Decision Outcome

Chosen option: **Hexagonal Architecture (Ports and Adapters)**.

### Reasoning
*   **Decoupling**: It isolates the core domain logic (`domain/`) from external concerns (`infrastructure/`, `presentation/`).
*   **Testability**: Ports (Interfaces) allow us to easily swap real implementations with mocks during testing.
*   **Flexibility**: We can change the database (e.g., from SQLite to Supabase) or the messaging provider (Twilio to WhatsApp Cloud API) by writing a new adapter without touching the business logic.

### Structure Implemented
*   `domain/`: Entities, Value Objects, Port Interfaces, Custom Errors.
*   `application/`: Use Cases, Service Orchestration (`LeadProcessor`).
*   `infrastructure/`: Adapters (Supabase, Twilio, Mistral), Logging.
*   `presentation/`: Entry points (FastAPI, CLI).
*   `config/`: Dependency Injection Container.

### Positive Consequences
*   Code is significantly easier to test (verified by passing unit test suite).
*   Clear modular boundaries.
*   Compliant with modern Python development standards (Pydantic, typing).

### Negative Consequences
*   Increased file count and initial complexity.
*   Requires boilerplate for Ports and Adapters.
