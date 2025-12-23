# ADR-035: Multi-language Support Strategy

## Status
Accepted

## Context
As the real estate agency operates in Tuscany, a significant portion of its leads are international tourists or foreign investors. The system needs to distinguish between local Italian-speaking leads and international English-speaking leads to provide a tailored experience.

## Decision
We implemented an automated language detection and persona switching mechanism.

### 1. Detection Mechanism
- **Phone Prefix**: Leads with non-Italian prefixes (non `+39`) default to English.
- **Keyword Detection**: If the user's input contains common English keywords (e.g., "looking", "house", "price"), the system switches to English.
- **Default**: Italian is the default for local numbers unless English is explicitly detected.

### 2. Persona Switching
- **Italian Persona**: A professional but friendly local agent, emphasizing local knowledge and "agency vibe."
- **English Persona**: A welcoming guide for tourists/investors, focused on the charm of Tuscany and explaining Italian real estate processes clearly to foreigners.

### 3. Implementation
The logic is centralized in the `ingest_node` of the LangGraph workflow and respected by the `generation_node` via system prompt instructions.

## Consequences
- **User Experience**: International leads feel welcomed in their own language, while local leads receive a standard professional service.
- **Maintenance**: Persona prompts must be maintained in both languages.
- **Complexity**: Adds a small detection overhead to the ingestion phase.
