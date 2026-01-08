# ADR-058: Landing Page UI/UX Standardization and Multi-page Migration

**Status:** Accepted
**Date:** 2026-01-07
**Author:** Antigravity (AI Assistant)

## 1. Context (The "Why")
The original landing page evolved into a complex mix of information, lead capture, and appraisal tools. The single-page architecture became difficult to maintain, especially when adding authentication flows (Login, Reset Password). Furthermore, layout shifts between Italian and English translations caused UI glitches in the sticky header.

## 2. Decision
Migrate the frontend to a **structured multi-page architecture** with standardized UI components.

Key components:
1.  **Decomposed Pages**: Break out functional areas into separate HTML files: `index.html` (Landing), `login.html`, `register.html`, `forgot-password.html`, `reset-password.html`, and `appraisal/index.html`.
2.  **Standardized Header**: Implement a fixed-height header CSS pattern to prevent "popping" or layout shifts when switching between languages or navigating between pages.
3.  **Auth Context persistence**: Standardize the use of `localStorage` via `auth-helper.js` to track user sessions across different sub-pages.
4.  **UI Refinement**: Standardize Call-to-Action (CTA) language (e.g., from "Prenota Demo" to "Contattaci") across all entry points for better conversion tracking.

## 3. Rationale (The "Proof")
*   **Maintainability**: Separate files for Login/Register make it easier to debug specific flows without scrolling through thousands of lines of HTML.
*   **SEO & UX**: Standard URLs for `/login` and `/forgot-password` are better for browser history and indexing.
*   **Visual Polish**: Fixed dimensions for headers ensure a premium "app-like" feel, consistent with the "Rich Aesthetics" goal.

## 4. Consequences
*   **Positive**: Cleaner codebase, consistent branding, improved accessibility, and no more "jumpy" navigation menus.
*   **Negative/Trade-offs**: Requires more careful management of shared assets (header/footer) until a full component-based framework (like Vite/React) is adopted.

## 5. Wiring Check (No Dead Code)
- [x] New pages created in `apps/landing-page/`
- [x] Header height standardized in `styles.css`
- [x] Login button repositioned and updated with icon in `index.html`
- [x] Obsolete `stats-grid-section` removed to reduce clutter
