# OMI Data Acquisition Guide

This guide outlines how to acquire OMI (Osservatorio del Mercato Immobiliare) datasets for use in the Fifi AI Appraisal tool.

## 1. Official Source (Ground Truth)
The primary and official source is the **Agenzia delle Entrate** (Italian Revenue Agency).

### Manual Download Process
1. **Access**: Log in to the [Reserved Area](https://www.agenziaentrate.gov.it/) (Entratel/Fisconline).
2. **Navigation**: Go to `Servizi > Fabbricati e Terreni > Forniture dati OMI`.
3. **Data Types**:
   - **Quotazioni immobiliari**: CSV files with min/max prices per sqm by zone.
   - **Volumi di compravendita (NTN)**: Annual transaction volumes at the municipal level.
   - **Perimetri Zone OMI**: KML files defining the geographic boundaries of OMI zones.
4. **Frequency**: Updated every 6 months (semesters).

> [!IMPORTANT]
> OMI data has a **6-month lag**. It should be used for historical "ground truth" training and not as a live market price source. For live data, continue using the `IdealistaMarketAdapter`.

## 2. Automation & APIs (Experimental)
Since the official portal requires authentication and manual interaction, consider these automated alternatives:

### Unofficial APIs
- **3euroTools API**: Offers a free REST API for OMI quotations.
  - **URL**: `https://3eurotools.it/api/omi` (Check documentation for attribution requirements).
- **Custom Scraper**: Automating the [GEOPOI service](https://mofp.agenziaentrate.gov.it/geopoi_omi/) to fetch zone perimeters.

### Open Data Portals
- **dati.gov.it**: Some OMI datasets (perimeters) are occasionally published as Open Data here, though they may not be the most recent.

## 3. Integration Strategy
Based on [ADR-040](file:///Users/lycanbeats/Desktop/agenzia-ai/docs/adr/ADR-040-fifi-avm-development-and-test-strategy.md), OMI data should be used to:
1. Ground truth the XGBoost model using the `zone_slug` matching the OMI zone code.
2. Provide legal transparency for the "Confidence Score".
3. Calculate the "Scraping Bias" (gap between asking prices and final sale prices).

## 4. Next Steps
1. [ ] Create a script to ingest OMI CSVs into `historical_transactions` table.
2. [ ] Map OMI Zone Codes to internal `zone_slug`s used in `generate_synthetic_data.py`.
3. [ ] Register a dedicated service account on the Agenzia delle Entrate portal for the agency.
