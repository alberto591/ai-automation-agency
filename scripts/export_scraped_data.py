import os
import sys
from datetime import datetime, timedelta

from dotenv import load_dotenv
from supabase import create_client

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import settings

load_dotenv()


def export_recent_properties():
    key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY
    if not key:
        print("❌ SUPABASE_KEY missing")
        return

    db = create_client(settings.SUPABASE_URL, key)

    # Fetch properties created in the last hour (covering the run)
    one_hour_ago = (datetime.utcnow() - timedelta(hours=1)).isoformat()

    try:
        res = db.table("properties").select("*").gte("created_at", one_hour_ago).execute()
        properties = res.data

        filename = f"scraped_properties_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        with open(filename, "w", encoding="utf-8") as f:
            f.write("# 🏠 Scraped Properties Report\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Total Parsed:** {len(properties)}\n\n")
            f.write("| Zone | Title | Price | Sqm | Link |\n")
            f.write("|---|---|---|---|---|\n")

            for p in properties:
                # Extract zone from description if possible (hacky parsing based on our injection)
                desc = p.get("description", "")
                zone = "Unknown"
                if "📍 ZONA:" in desc:
                    try:
                        zone = desc.split("📍 ZONA:")[1].split(",")[0].strip()
                    except:
                        pass

                title = p.get("title", "No Title").replace("|", "-")
                price = f"€{p.get('price'):,.0f}" if p.get("price") else "N/A"
                sqm = f"{p.get('sqm')} m²" if p.get("sqm") else "N/A"
                # constructing a link if possible, otherwise just use title

                f.write(f"| {zone} | {title} | {price} | {sqm} | [Image]({p.get('image_url')}) |\n")

        print(f"✅ Exported {len(properties)} properties to {filename}")
        print(f"::set-output name=report_file::{filename}")

    except Exception as e:
        print(f"❌ Error exporting data: {e}")


if __name__ == "__main__":
    export_recent_properties()
