# Fixes Applied

Comprehensive log of fixes and improvements made to the Anzevino AI project.

---

## 2025-12-31: Frontend Separation & Testing

### Frontend Architecture Refactor
- **Separated monolithic frontend** into 3 independent apps:
  - `apps/landing-page` → Marketing site at `/`
  - `apps/dashboard` → Admin panel at `/dashboard`
  - `apps/fifi` → Appraisal tool at `/appraisal`

### Vite Configuration Fixes
- Added `base: '/appraisal/'` to `apps/fifi/vite.config.js`
- Verified `base: '/dashboard/'` in `apps/dashboard/vite.config.js`
- Ensured asset paths resolve correctly after deployment

### Navigation Updates
- Updated `apps/fifi/index.html` nav to link to `/` and `/dashboard`
- Updated `apps/landing-page/index.html` nav to link to `/dashboard` and `/appraisal`
- Replaced Fifi interactive tool with CTA button on landing page

### Content Isolation
- Removed Hero, Problem, Video Demo, Features, Contact sections from Fifi
- Fifi now shows only the appraisal tool interface

### Build Configuration
- Updated `vercel.json` to orchestrate multi-app builds
- Build outputs merged into single `dist/` directory

### Test Coverage Added
- `test_generate_appraisal_pdf_success` - PDF generation success
- `test_generate_appraisal_pdf_failure` - Error handling
- `test_generate_appraisal_estimate` - Estimation endpoint
- Added `appraisal_service` mock to `conftest.py`

### Legacy Code Archived
- Moved `appraisal-tool/` to `archive/legacy_appraisal-tool/`

---

## 2025-12-30: Regulatory Hardening & Legal Prep

### Disclaimer Enforcement
- Added mandatory click-to-accept disclaimer in appraisal form
- Client-side validation blocks submission without acceptance

### Form Validation
- Phone number format validation
- Required field enforcement
- Error message display improvements

---

## Earlier Fixes

### Claude.md Refactoring
- Updated from "UK Family Law AI" to "Anzevino AI Real Estate Agent"
- Changed embedding standard from 768D Gemini to 1024D Mistral
- Updated pattern examples to real estate context
- Fixed file path references

### Best Practices Module
- Added real estate-specific patterns (LEAD_QUALIFICATION, AVM_INTEGRATION)
- Updated `best_practices/__init__.py` with new patterns
- Fixed ruff lint errors in `create_doc.py`

### Documentation Organization
- Created `docs/doc_manifest.json` for file organization rules
- Added `scripts/docs/create_doc.py` CLI helper
- Cleaned up root markdown file proliferation

---

*Last updated: 2025-12-31*
