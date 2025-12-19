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

The import is performed using the `upload_data.py` script. You must use the project's virtual environment.

### Option A: Use the Sample File
```bash
venv/bin/python3 upload_data.py --csv properties_sample.csv
```

### Option B: Use your own CSV
```bash
venv/bin/python3 upload_data.py --csv /path/to/your_file.csv
```

## ✅ Verification
1.  **Terminal Output**: Check for `✅ [Success] Sync completed!`.
2.  **AI Testing**: Ask the AI via WhatsApp "Do you have any apartments in [Your Area]?" to verify it matches your data.

## 🛠️ Troubleshooting
- **Invalid Price**: Ensure the `price` column contains ONLY numbers.
- **Encoding**: Ensure your CSV is saved with **UTF-8** encoding.
