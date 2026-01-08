# ADR-057: Supabase-based User Authentication and Security Model

**Status:** Accepted
**Date:** 2026-01-07
**Author:** Antigravity (AI Assistant)

## 1. Context (The "Why")
As the application scales from a simple landing page to a multi-agency platform, we require a robust way to manage user identities, agency profiles, and data isolation. Specifically, we need to ensure that leads captured for one agency are not visible to others, and provide a secure mechanism for password resets and profile management.

## 2. Decision
Implement a comprehensive Authentication and Authorization layer using **Supabase Auth** integrated with a custom **PostgreSQL** schema.

Key components:
1.  **Extended User Profiles**: Create a `public.user_profiles` table that references `auth.users(id)` to store agency-specific metadata (Agency Name, Phone).
2.  **Row Level Security (RLS)**: Enforce strict isolation on the `leads` table. Every lead is now linked to an `agency_id`, and RLS policies ensure users can only `SELECT`, `INSERT`, or `UPDATE` leads belonging to their own agency.
3.  **Automated Profile Creation**: Use a Postgres Trigger (`on_auth_user_created`) to automatically create a entry in `user_profiles` whenever a new user signs up via Supabase.
4.  **Client-Side Integration**: Use `auth-helper.js` to wrap Supabase client calls, providing a consistent API for login, registration, and password recovery (`forgot-password.html`, `reset-password.html`).

## 3. Rationale (The "Proof")
*   **Security by Default**: RLS moves the security boundary from the application layer to the database layer, preventing "broken object level authorization" bugs.
*   **Reduced Complexity**: Leveraging Supabase Auth handles the complexities of JWT management, email confirmation, and password hashing.
*   **Extensibility**: The `user_profiles` table allows us to add more agency-specific fields (e.g., logo, subscription tier) without affecting the core auth system.

## 4. Consequences
*   **Positive**: Secure multi-tenancy, standardized auth flow, and automated data synchronization between auth and application domains.
*   **Negative/Trade-offs**: Requires client-side JS to maintain session state; non-authenticated requests to the DB are now strictly blocked by default.
*   **Migration**: Existing leads must be manually assigned to an `agency_id` (defaulting to a 'demo' agency for existing orphaned leads).

## 5. Wiring Check (No Dead Code)
- [x] Schema defined in `docs/sql/20260107_user_authentication.sql`
- [x] Logic implemented in `apps/landing-page/auth-helper.js`
- [x] RLS policies applied to `user_profiles` and `leads`
- [x] Scripts for admin management created: `scripts/create_admin_user.py`
