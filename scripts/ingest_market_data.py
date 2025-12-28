import os
import re
import sys
from typing import Any

# Add root to path
sys.path.append(os.getcwd())

from infrastructure.adapters.supabase_adapter import SupabaseAdapter
from infrastructure.logging import get_logger

logger = get_logger(__name__)


def parse_markdown_table(file_path: str) -> list[dict[str, Any]]:
    """
    Parses the property table from the markdown report.
    """
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return []

    properties = []
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    # Find the table start (header row)
    start_index = -1
    for i, line in enumerate(lines):
        if "| Zone | Title | Price | Sqm | Link |" in line:
            start_index = i + 2  # Skip header and separator row
            break

    if start_index == -1:
        print("❌ Could not find the properties table in the markdown file.")
        return []

    for line in lines[start_index:]:
        if not line.strip() or not line.startswith("|"):
            continue

        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 6:
            continue

        # Parts format: ['', Zone, Title, Price, Sqm, Link, '']
        zone = parts[1]
        title = parts[2]
        price_str = parts[3]
        sqm_str = parts[4]
        link_str = parts[5]

        # Extract numeric values
        # Price: €248,000 -> 248000
        price = None
        price_match = re.search(r"€([\d,]+)", price_str)
        if price_match:
            price = float(price_match.group(1).replace(",", ""))

        # Sqm: 27 m² -> 27
        sqm = None
        sqm_match = re.search(r"(\d+)", sqm_str)
        if sqm_match:
            sqm = float(sqm_match.group(1))

        # Link: [Image](url) -> url
        link = ""
        link_match = re.search(r"\[Image\]\((.*?)\)", link_str)
        if link_match:
            link = link_match.group(1)

        properties.append(
            {
                "zone": zone,
                "title": title,
                "price": price,
                "sqm": sqm,
                "portal_url": link,
                "price_per_mq": (price / sqm) if price and sqm and sqm > 0 else None,
            }
        )

    return properties


def main():
    report_file = "scraped_properties_20251223_175302.md"
    print(f"📖 Parsing {report_file}...")

    properties = parse_markdown_table(report_file)
    if not properties:
        return

    print(f"✅ Parsed {len(properties)} properties.")

    db = SupabaseAdapter()
    count = 0
    errors = 0

    print("🚀 Ingesting data into 'market_data' table...")
    for p in properties:
        try:
            # We use upsert on portal_url to avoid duplicates
            db.client.table("market_data").upsert(p, on_conflict="portal_url").execute()
            count += 1
            if count % 20 == 0:
                print(f"  Processed {count}...")
        except Exception as e:
            errors += 1
            # logger.error("MARKET_DATA_INGEST_FAILED", context={"title": p['title'], "error": str(e)})

    print("\n✨ Ingestion Complete!")
    print(f"📊 Total Added/Updated: {count}")
    print(f"❌ Errors: {errors}")


if __name__ == "__main__":
    main()
