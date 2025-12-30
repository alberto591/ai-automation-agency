# ADR-044: PDF Appraisal Report Generation

**Status:** Accepted
**Date:** 2025-12-30
**Author:** Antigravity AI

## 1. Context (The "Why")
Users of the AI Appraisal Tool need a professional, downloadable record of their property valuation. While the instant UI results and WhatsApp delivery are valuable, high-intent leads expect a formal document for reference, printing, or sharing with financial institutions.

The report needs to include:
- Property identification (address/postcode).
- Professional valuation with confidence ranges.
- Detailed investment metrics (Cap Rate, ROI, Cash-on-Cash).
- Market comparables for grounding.
- Legal disclaimers for compliance.

## 2. Decision
We have implemented a dedicated PDF generation pipeline using the `fpdf2` library.

Specific technical implementations:
1.  **Backend Generator**: Extended `PropertyPDFGenerator` in `infrastructure/ai_pdf_generator.py` with a `generate_appraisal_report()` method.
2.  **API Endpoint**: Created a new `POST /api/appraisals/generate-pdf` endpoint in `presentation/api/api.py`.
3.  **Frontend Integration**: Added a "Scarica Report PDF" button to the appraisal results UI in `appraisal-tool/index.html`.
4.  **Encoding Strategy**: Switched to "EUR" text instead of the € symbol to avoid Unicode encoding failures with default PDF font sets (Helvetica), ensuring zero dependency on external font files for initial launch.
5.  **Dynamic Data Flow**: The frontend now sends the calculated or simulated `fifi_data` directly to the API, ensuring consistency between what the user sees on screen and what is printed in the PDF.

## 3. Rationale (The "Proof")
- **fpdf2**: Already present in the environment (`document_adapter.py` dependency). It is lightweight, requires no heavy external dependencies (like wkhtmltopdf or headless browsers), and is perfect for structured, template-based reports.
- **Client-Side Data Source**: Since the landing page form currently performs client-side simulation for instant "lead magnet" results, sending this data to the PDF generator ensures the user receives exactly what they saw, even if backend ML inference is still processing asynchronously for the WhatsApp delivery.
- **"EUR" vs €**: During testing, the Helvetica font threw `UnicodeEncodeError` with the Euro symbol. Using "EUR" provides 100% reliability across all PDF readers without increasing file size or complexity with embedded UTF-8 fonts.

## 4. Consequences
- **Positive**:
    - Increased lead perceived value.
    - Professional branding for Anzevino AI.
    - Offline accessibility for appraisal results.
- **Negative/Trade-offs**:
    - The PDF structure is currently hardcoded in Python; changes to the template require code modifications rather than simple HTML/CSS edits.
    - Files are currently stored locally in `temp/documents/`. A future migration to Supabase Storage will be required for production durability.

## 5. Wiring Check (No Dead Code)
- [x] Generator implemented in `infrastructure/ai_pdf_generator.py`
- [x] Endpoint exposed in `presentation/api/api.py`
- [x] UI button implemented in `appraisal-tool/index.html`
- [x] Client logic implemented in `appraisal-tool/script.js`
- [x] Unit tests added in `tests/unit/test_pdf_generator.py`
- [x] Requirements updated (fpdf2)
