-- ==========================================
-- Fix: Optimized Invitation Trigger (Before Insert)
-- Migration: 20260114_fix_invite_trigger.sql
-- ==========================================

-- Function to handle invitation acceptance
-- We switched to BEFORE INSERT to set metadata directly on the new user object
-- This prevents race conditions and recursively updating auth.users
CREATE OR REPLACE FUNCTION public.handle_invite_before_insert()
RETURNS TRIGGER AS $$
DECLARE
    invite RECORD;
BEGIN
    -- Check for pending invitation
    SELECT * INTO invite
    FROM public.organization_invitations
    WHERE email = NEW.email
    AND accepted_at IS NULL
    AND expires_at > NOW()
    ORDER BY created_at DESC
    LIMIT 1;

    IF invite IS NOT NULL THEN
        -- 1. Set the Metadata directly on the NEW row
        -- This ensures the user is created with this metadata instantly
        NEW.raw_app_meta_data := COALESCE(NEW.raw_app_meta_data, '{}'::jsonb) ||
            jsonb_build_object('active_org_id', invite.organization_id::text);

        -- 2. Mark invitation as accepted (Side Effect)
        UPDATE public.organization_invitations
        SET accepted_at = NOW()
        WHERE id = invite.id;

        -- 3. We STILL need to add them to the members table.
        -- We CANNOT do this in BEFORE INSERT accurately because the user ID might not exist in FK constraints yet?
        -- Actually, strictly speaking, auth.users primary key is generated before...
        -- BUT, referenced tables usually check constraints at end of statement.
        -- However, inserting into `organization_members` requires the User ID.
        -- Attempting to insert into a related table inside a BEFORE INSERT trigger *can* work if the ID is pre-generated (uuid).
        -- Safe bet: Split logic.
        -- Metadata -> BEFORE INSERT
        -- Members Table Link -> AFTER INSERT
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


CREATE OR REPLACE FUNCTION public.handle_invite_after_insert()
RETURNS TRIGGER AS $$
DECLARE
    invite RECORD;
BEGIN
    -- Re-fetch to be safe, or we could rely on metadata if we trust it, but searching invite is safer source of truth
    SELECT * INTO invite
    FROM public.organization_invitations
    WHERE email = NEW.email
    -- Look for the one we just 'accepted' (accepted_at is NOW() roughly)
    -- OR just find the valid one. Since we updated accepted_at in BEFORE trigger, we can find it by that?
    -- Actually, sharing state between triggers is hard.
    -- Let's just find the invite that matches the org_id in the metadata we just set?
    -- OR, safer: Just check for the invite again.
    -- Problem: The BEFORE trigger marked it accepted.
    AND accepted_at >= (NOW() - INTERVAL '1 minute')
    ORDER BY accepted_at DESC
    LIMIT 1;

    IF invite IS NOT NULL THEN
        -- Add user to organization members
        INSERT INTO public.organization_members (user_id, organization_id, role)
        VALUES (NEW.id, invite.organization_id, invite.role)
        ON CONFLICT DO NOTHING;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- Drop old triggers/functions
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS public.handle_new_user_invitation();

-- Attach New Triggers
CREATE TRIGGER on_auth_user_created_metadata
    BEFORE INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_invite_before_insert();

CREATE TRIGGER on_auth_user_created_link
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_invite_after_insert();
