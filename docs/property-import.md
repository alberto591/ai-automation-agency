# Property Import Guide (CSV)

This guide explains how to use the automated CSV importer to update your agency's property portfolio in Supabase. This data directly powers the AI's ability to match properties to leads.

## 📝 CSV Format Requirements

The importer expects a file named `properties_sample.csv` (or any other `.csv` file) with the following mandatory columns:

| Column | Description | Example |
| :--- | :--- | :--- |
| **title** | A descriptive name for the property. | *Attico Moderno Porta Nuova* |
| **description** | Details about size, rooms, features, and location. | *90mq, 2 bedrooms, balcony, recently renovated.* |
| **price** | The numeric price (no currency symbols or dots). | *450000* |

> [!NOTE]
> Values containing commas (like descriptions) must be enclosed in double quotes: `"Spacious room, 20mq, with view"`.

## 🚀 How to Run the Import

The import is performed using the `scripts/seed_properties.py` script. You must use the project's virtual environment.

### Option A: Upload to PRODUCTION
This will add properties to your live database used by the AI.
```bash
./venv/bin/python3 scripts/seed_properties.py --prod --file your_properties.csv
```

### Option B: Upload to MOCK (Testing)
Safe for testing new data without affecting the live customer experience.
```bash
./venv/bin/python3 scripts/seed_properties.py --mock --file your_properties.csv
```

### Option C: Clear Mock data
```bash
./venv/bin/python3 scripts/seed_properties.py --clear-mock
```

## ✅ Verification
1.  **Terminal Output**: Check for `✅ [Success] Sync completed!`.
2.  **AI Testing**: Ask the AI via WhatsApp "Do you have any apartments in [Your Area]?" to verify it matches your data.

## 🛠️ Troubleshooting
- **Invalid Price**: Ensure the `price` column contains ONLY numbers.
- **Encoding**: Ensure your CSV is saved with **UTF-8** encoding.
