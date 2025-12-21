# 11. Market Data Scraping Strategy

* Status: Accepted
* Deciders: Engineering Team, Antigravity Agent
* Date: 2024-03-01 (Retroactive)

## Context and Problem Statement

To provide value to property owners, the agency needs to offer market insights (e.g., "Your price is 10% below the average for this zone"). This requires up-to-date data on comparable listings from major portals like Immobiliare.it.

## Considered Options

*   **Commercial APIs**: Buying access to real estate data providers (often expensive or have strict TOS).
*   **Custom Scrapers**: Building internal Python scripts to parse public portal pages.
*   **Manual Entry**: Agents manually inputting competitor data.

## Decision Outcome

Chosen option: **Custom Scrapers**.

### Reasoning
1.  **Cost**: Commercial APIs for this data are prohibitively expensive for a small agency.
2.  **Granularity**: We need specific fields (Energy Class, Floor, Condo Fees) that generic APIs might miss.
3.  **Control**: By writing our own `BeautifulSoup` parsers, we can adapt to layout changes immediately.

### Implementation
*   `infrastructure/market_scraper.py`: Modular scraper class.
*   **Rate Limiting**: Implementation of delays and User-Agent rotation to be polite to target servers.
*   **Storage**: Data is upserted into Supabase `market_data` table for analysis.

### Positive Consequences
*   Zero marginal cost for data acquisition.
*   Data ownership (we build our own historical dataset).

### Negative Consequences
*   Maintenance burden (scrapers break when site layouts change).
*   Legal/TOS gray area (must strictly follow robots.txt and not republish data).
