# Client Onboarding Guide

Current Protocol: **Manual SQL via Supabase**
*Goal: Create a new tenant (Organization) and invite their Admin user.*

---

## 🚀 Quick Steps

Run the following SQL block in your [Supabase SQL Editor](https://supabase.com/dashboard/project/_/sql):

```sql
-- 1. Create the Organization
WITH new_org AS (
    INSERT INTO organizations (name, slug, plan)
    VALUES (
        'Client Name',        -- REPLACE THIS
        'client-slug',        -- REPLACE THIS (must be unique URL-safe)
        'pro'                 -- 'free', 'pro', or 'enterprise'
    )
    RETURNING id
)
-- 2. Create the Invitation
INSERT INTO organization_invitations (organization_id, email, role)
SELECT
    id,
    'client@example.com',     -- REPLACE THIS (Client's Email)
    'owner'                   -- Role: 'owner' or 'admin'
FROM new_org;
```

---

## 📋 Detailed Process

### 1. Define the Organization
You must create a row in the `organizations` table.
- **Name**: Display name (e.g., "Prestige Estate Agents").
- **Slug**: Unique identifier for URLs (e.g., "prestige-estates").

### 2. Prepare the Invite
The `organization_invitations` table handles the security link.
- **Email**: The email address the client MUST use to sign up.
- **Role**: usually `'owner'` for the first user of an agency.

### 3. Client Action
1.  Notify the client that they have been invited.
2.  Direct them to your signup URL: `https://your-app-url.com/signup` (or local `http://localhost:5173/signup`).
3.  They **MUST** use the exact email address you invited.
4.  They can choose any password.

**Result:** The system triggers `handle_invite_before_insert`, automatically assigning them to the correct Organization and isolating their data.

---

## 🔍 Verification

To verify a client was onboarded correctly, run:

```sql
SELECT u.email, om.role, o.name as organization
FROM auth.users u
JOIN organization_members om ON u.id = om.user_id
JOIN organizations o ON om.organization_id = o.id
WHERE u.email = 'client@example.com'; -- Replace with client email
```

If a row returns, they are successfully onboarded.

## 🛠 Troubleshooting

**Issue: Client sees an empty dashboard but shouldn't (or sees errors).**
- Check if they signed up with a different email (case-sensitive in some DBs, though usually normalized).
- Check if the invitation expired (default 7 days).
- **Fix:** If they signed up *before* you invited them, or if the trigger failed:
    ```sql
    -- Manually Link User
    INSERT INTO organization_members (user_id, organization_id, role)
    SELECT u.id, o.id, 'owner'
    FROM auth.users u, organizations o
    WHERE u.email = 'client@example.com' AND o.slug = 'client-slug';

    -- Fix Metadata
    UPDATE auth.users
    SET raw_app_meta_data = raw_app_meta_data ||
        jsonb_build_object('active_org_id', (SELECT id FROM organizations WHERE slug = 'client-slug'))
    WHERE email = 'client@example.com';
    ```
