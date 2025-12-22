# ADR-032: Real Market Data Integration

## Status
Accepted

## Context
The AI Agent initially used mocked or hardcoded data for property valuations. To build trust with users and provide "Wow" factor in demos, the system needs deeper market awareness.

## Decision
We decided to integrate **Idealista Market Data** via the `IdealistaMarketAdapter` as the primary source of truth for valuations, with a fallback to "Expert Data" (hardcoded regional averages) for stability.

### Implementation
- **Adapter**: `IdealistaMarketAdapter` implements `MarketDataPort`.
- **Primary Source**: RapidAPI (Idealista unofficial or similar) for live data.
- **Fallback strategy**: If API fails or credit limit reached, use `EXPERT_DATA` (e.g., Tuscany region averages).
- **LangGraph Integration**: A dedicated `market_analysis_node` injects this data into the context for `WEB_APPRAISAL` and negotiation phases.

## Alternatives Considered
- **Immobiliare.it Scraping**: Rejected due to higher blocking risk and legal gray areas for automated valuation.
- **OMI Database (Agenzia Entrate)**: Official but often outdated (6-month lag).
