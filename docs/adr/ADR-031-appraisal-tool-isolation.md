# ADR-031: Appraisal Tool Isolation

## Status
Accepted

## Context
The project initially colocated the AI Appraisal Tool (frontend) within a `landing_page/` directory, which was deployed as part of the main dashboard application. As the project grew, the Appraisal Tool evolved into a distinct "Acquisition Product" with its own lifecycle, separate from the "Management Product" (Dashboard).

The monolithic structure caused confusion in deployment configuration (Vercel rewrites) and mixed concern between the consumer-facing funnel and the agent-facing CRM.

## Decision
We decided to isolate the Appraisal Tool into a top-level directory named `appraisal-tool/`.

### Consequences
- **Directory Structure**: `landing_page/` is renamed to `appraisal-tool/`.
- **Deployment**: Vercel configuration must be updated to serve `appraisal-tool/` as a distinct route or standalone build, ensuring clear separation from the Dashboard (`dashboard/`).
- **Docs**: Documentation must be updated to reflect the new Architecture (e.g., `appraisal-tool-architecture.md`).
- **Separation of Concerns**: Clearer boundary between "Lead Gen" (Appraisal) and "Lead Ops" (Dashboard).

## Alternatives Considered
- **Monorepo with Turborepo**: Considered overkill for the current team size.
- **Keep in Landing Page**: Rejected as "Landing Page" is too generic and doesn't reflect the tool's specialized function (AI Valuation).
