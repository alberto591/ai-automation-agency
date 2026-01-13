# Lead Data Storage & Visibility

This guide documents where lead data is stored, how to access it, and specifically handles the **Agency Demo** leads captured from the landing page.

## 1. Google Sheets (Operational View)
The system is configured to automatically sync every new lead to a Google Sheet. This is the easiest way to view incoming data in real-time.

- **Sync Trigger**: Happens immediately after the AI processes the lead.
- **Data Synced**: Phone, Name, Status, Last Message/Notes.
- **Current Sheet**: [Open Spreadsheet](https://docs.google.com/spreadsheets/d/1TYyvnFy6QxQJYiQvvkMdvpIQ5ApzwIxKvXe0hAb8GxI)
  - *Note: To verify the active Sheet ID, check the backend logs for the `GOOGLE_SHEETS_CONNECTED` event.*

## 2. Supabase Database (System of Record)
All leads are permanently stored in the Postgres database.

### Table: `leads`

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid | Unique ID |
| `customer_phone` | text | Primary Key |
| `customer_name` | text | Name (e.g., "John Doe") |
| `metadata` | jsonb | **Rich Data & Context** |
| `created_at` | timestamptz | Timestamp |

### Agency Demo Data Structure
When an agency requests a demo via the **"Book Free Demo"** button, the data is stored specifically in the `metadata` column to preserve the extra context (Agency Name).

**JSON Structure:**
```json
{
  "source": "AGENCY_DEMO",
  "context_data": {
    "agency_name": "My Real Estate Agency"
  },
  "preferences": { ... },
  "sentiment": { ... }
}
```

### Useful SQL Queries

**Find all Agency Demos:**
```sql
SELECT 
    customer_name,
    customer_phone,
    metadata->'context_data'->>'agency_name' as agency_name,
    created_at
FROM leads
WHERE metadata->>'source' = 'AGENCY_DEMO'
ORDER BY created_at DESC;
```

**Find all Leads (General):**
```sql
SELECT * FROM leads ORDER BY created_at DESC;
```

## 3. Data Flow Verification
1. **Frontend**: submitting the form sends a POST to `/api/leads`.
2. **Backend**: 
    - `LeadProcessor` routes the request.
    - `ingest_node` creates/updates the lead record.
    - `finalize_node` updates the `metadata` with the extracted `Agency Name` and syncs to Google Sheets.
