# Production Data Gathering Guide

This guide documents the process for gathering production-ready real estate data using the Agency AI Scraper.

## Overview

The scraper (`scripts/gather_production_data.py`) gathers real-time property listings from **Idealista** via RapidAPI. It bypasses direct scraping protections by using an authorized API, ensuring reliable access to high-quality data.

- **Source**: Idealista (via RapidAPI)
- **Target Zones**: Milano (Centro, Isola, Navigli), Firenze, Chianti, and configurable others.
- **Destinations**: Supabase `properties` table.

## Prerequisites

1.  **RapidAPI Key**: Ensure `RAPIDAPI_KEY` is set in your `.env` file.
    ```bash
    RAPIDAPI_KEY=your_key_here
    ```
2.  **Supabase Service Key**: The script requires `SUPABASE_SERVICE_ROLE_KEY` to bypass Row Level Security (RLS) policies during bulk upserts.
    ```bash
    SUPABASE_SERVICE_ROLE_KEY=your_service_key_here
    ```

## Usage

Run the gathering script from the project root:

```bash
./venv/bin/python scripts/gather_production_data.py
```

By default, the script runs for **30 minutes**. You can adjust the `duration_minutes` parameter in the `run_gathering` function call within the script.

## Data Schema & Normalization

The scraper automatically maps API data to the Agency AI normalized schema.

| API Field | Database Column | Notes |
| :--- | :--- | :--- |
| `price` | `price` | Converted to float |
| `size` | `sqm` | Converted to float |
| `rooms` | `rooms` | Integer |
| `floor` | `floor` | Parsed from string (e.g., "1st" -> 1) |
| `thumbnail` | `image_url` | Used for duplicate usage check |
| `propertyCode` | N/A | Ignored; `image_url` used as unique key |

**Note**: To improve searchability, the `zone` and `city` are injected into the `description` field, as the current `properties` table schema may not support distinct location columns.

## Preventing Duplicates

The script implements a manual "check-before-insert" logic:

1.  Extracts `image_url` from the API response.
2.  Queries the `properties` table to see if a record with that `image_url` already exists.
3.  If found, the listing is skipped to prevent duplicates.

## Exporting Reports

To generate a summary report of recently scraped properties:

```bash
./venv/bin/python scripts/export_scraped_data.py
```

This will create a Markdown report (e.g., `scraped_properties_YYYYMMDD_HHMMSS.md`) listing all properties ingested in the last hour.
