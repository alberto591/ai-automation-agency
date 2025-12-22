# Database Standards & Architecture - Real Estate AI

## 1. Introduction for Non-Experts
A database isn't just a spreadsheet; it's the brain of your application. For this project, we use **PostgreSQL** (via Supabase), which is the industry standard for reliability.

### Core Concepts
- **Tables**: Like tabs in a spreadsheet (e.g., `properties`, `leads`).
- **Columns**: specific data points (e.g., `price`, `sqm`).
- **Rows**: Individual records (e.g., a specific apartment).
- **Primary Key (PK)**: A unique ID for every single row (usually a UUID like `123e4567-e89b...`).
- **Foreign Key (FK)**: A link between tables (e.g., a property belongs to an owner).

---

## 2. Naming Conventions (The "Grammar")
Consistency makes the database easy to read.

| Object | Convention | Example | Why? |
| :--- | :--- | :--- | :--- |
| **Tables** | Plural, snake_case | `lead_conversations`, `properties` | Represents a collection of items. |
| **Columns** | Singular, snake_case | `customer_phone`, `is_ai_active` | Represents a single attribute. |
| **Primary Keys** | `id` | `id` | Simple and standard. |
| **Foreign Keys** | `noun_id` | `property_id`, `user_id` | Clear indication of what it points to. |
| **Booleans** | `is_` or `has_` | `is_active`, `has_elevator` | Reads like a question (True/False). |

---

## 3. Current Project Schema (As of Dec 2025)

### `properties` (The Inventory)
Used to store all real estate listings.
- `id` (UUID, PK): Unique identifier.
- `title` (TEXT): Marketing title.
- `price` (FLOAT/INT): Asking price.
- `status` (TEXT): 'available', 'reserved', 'sold'.
- `specs`: `sqm`, `rooms`, `bathrooms`, `floor` (Integers).
- `features`: `has_elevator`, `energy_class`.

### `lead_conversations` (The CRM)
Stores potential clients and the AI chat history.
- `id` (UUID, PK): Unique identifier.
- `customer_phone` (TEXT, Unique): The main way we identify users.
- `messages` (JSONB): The entire chat history stored as a structured list.
- `status` (TEXT): 'active', 'hot', 'human_mode'.
- `is_ai_active` (BOOLEAN): **Critical** for the AI toggle features.
- `preferences`: `budget_max`, `preferred_zones`.

### `market_data` (Competitive Intelligence)
Stores scraped data from other portals.
- `portal_url` (TEXT): Source of the data.
- `price_per_mq` (FLOAT): Analytic metric.

---

## 4. Best Practices for This Project

### 4.1. Use `JSONB` for Chat History
Instead of a separate table for every single message (`messages` table), we store the conversation as a `JSONB` array in the `lead_conversations` table.
- **Pro**: Much faster validation; easier for the AI context window.
- **Con**: Harder to search *inside* specific messages (but we solve this with AI search).

### 4.2. Row Level Security (RLS)
This is Supabase's superpower. It allows us to secure data at the database engine level.
*   **Rule**: "Only the Agency Owner can delete leads."
*   **Rule**: "Public can view properties, but only Agents can edit them."

### 4.3. Indexing
Indexes apply a "sort order" to data so the database can find it instantly without scanning everything.
*   We index `customer_phone` because we look it up on *every single webhook*.
*   We index `price` and `sqm` for fast filtering in the mobile app.

---

## 5. Future Roadmap (Recommended Structure)

If the project grows, we should split `lead_conversations` into two:
1.  **`leads`**: Just the person's info (Name, Phone, Budget).
2.  **`conversations`**: Just the chat logs.
*Why?* A lead might sell one house and buy another later. That's two conversations for one person.

## 6. Security Checklist
- [x] RLS Enabled on all public tables.
- [ ] No raw "Supabase Service Key" in frontend code (Backend only).
- [ ] Backups enabled in Supabase dashboard.
