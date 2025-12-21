# Fix: Enable Database Updates

## Problem
The system cannot save the image URL or AI-enriched data back to Supabase because the current API Key in your `.env` file (`SUPABASE_KEY`) is an **Anonymous Key**. This key is read-only for security reasons (Row Level Security).

## Solution
To allow the AI to update your database property records, you need the **Service Role Key**.

### Steps
1.  Go to your [Supabase Dashboard](https://supabase.com/dashboard/project/_/settings/api).
2.  Find the `service_role` key (secret).
3.  Open your `.env` file in the project root.
4.  Add the following line:

```bash
SUPABASE_SERVICE_ROLE_KEY=eyJh... (your secret key)
```

Once added, the scripts will automatically pick it up and be able to save your data permanently.
