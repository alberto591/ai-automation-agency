# 🗄️ Database Upgrade (Pro Dashboard)

To enable the **Pro Dashboard** features (full chat history, AI takeover, and consolidated leads), you need to add two columns to your Supabase `lead_conversations` table.

## 🚀 SQL Migration

Copy and paste the following SQL into your **Supabase SQL Editor**:

```sql
-- 1. Add JSONB column for full chat history
ALTER TABLE lead_conversations
ADD COLUMN IF NOT EXISTS messages JSONB DEFAULT '[]';

-- 2. Add updated_at column for proper sorting
ALTER TABLE lead_conversations
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- 3. [CLEANUP] Delete duplicate phone records (keeps only the most recent)
-- This is necessary before adding the UNIQUE constraint.
DELETE FROM lead_conversations
WHERE id NOT IN (
  SELECT id
  FROM (
    SELECT id, ROW_NUMBER() OVER (PARTITION BY customer_phone ORDER BY created_at DESC) as row_num
    FROM lead_conversations
  ) t
  WHERE t.row_num = 1
);

-- 4. Add the unique constraint to phone numbers
ALTER TABLE lead_conversations
ADD CONSTRAINT unique_customer_phone UNIQUE (customer_phone);
```

## ❓ Why is this needed?
- **Messages**: Stores the entire history of speech bubbles you see in the dashboard.
- **Updated At**: Ensures the leads who just texted appear at the top of your sidebar.
- **Unique Constraint**: Allows the backend to "update" an existing lead instead of creating a new row for every single WhatsApp message.

## 🛠️ After Migration
Once the columns are added, the backend will automatically stop using the "Fallback Mode" and start providing the full chat experience.
