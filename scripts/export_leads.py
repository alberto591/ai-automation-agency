import os
import csv
import sys
from dotenv import load_dotenv
from supabase import create_client

# Add parent directory to path to allow importing from root if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    print("❌ Error: Missing credentials.")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def export_leads():
    print("📊 Exporting Leads to 'leads_export.csv'...")
    
    try:
        # Fetch all leads (limit 1000 for safety)
        response = supabase.table("lead_conversations").select("*").order("created_at", desc=True).limit(1000).execute()
        leads = response.data
        
        if not leads:
            print("⚠️ No leads found in database.")
            return

        # Write to CSV
        with open("leads_export.csv", "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = leads[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for lead in leads:
                writer.writerow(lead)
                
        print(f"✅ Success! Exported {len(leads)} rows to leads_export.csv")
        
    except Exception as e:
        print(f"❌ Export Failed: {e}")

if __name__ == "__main__":
    export_leads()
