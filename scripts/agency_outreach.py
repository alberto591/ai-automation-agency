import csv

HEADERS: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def search_agencies(city: str = "Milano", pages: int = 1) -> list[dict[str, str]]:
    """
    Finds real estate agencies by extracting them from active market listings.
    """
    from infrastructure.market_service import MarketDataService

    print(f"🚀 Searching for Real Estate Agencies in {city}...")
    service = MarketDataService()
    listings = service.search_properties(zone=city, city=city)

    agencies = {}
    for item in listings:
        # Idealista API structure usually has 'contactName' and 'phone' or 'agencyName'
        # Let's try to extract what we can
        name = item.get("contactName") or item.get("agencyName") or item.get("agencyId")
        phone = item.get("phone")

        if name and phone and name not in agencies:
            # Clean name and phone
            clean_name = str(name).strip()
            clean_phone = str(phone).replace(" ", "")
            if not clean_phone.startswith("+"):
                clean_phone = f"+39{clean_phone}"  # Assume IT if no prefix

            agencies[clean_name] = {
                "name": clean_name,
                "phone": clean_phone,
                "address": item.get("address", "N/A"),
                "city": city,
            }

    results = list(agencies.values())
    print(f"✅ Found {len(results)} unique agencies from listings.")

    if not results:
        print("⚠️ No agencies found from live listings, using fallback.")
        return [
            {
                "name": "Milano Elite Properties",
                "phone": "+393401111111",
                "address": "Via Dante 10",
                "city": city,
            }
        ]

    return results


def generate_outreach_csv(
    agencies: list[dict[str, str]], filename: str = "outreach_targets.csv"
) -> None:
    """
    Saves agencies to a CSV with AI-personalized outreach messages.
    """
    from config.container import container

    keys = ["name", "phone", "address", "city", "outreach_message"]

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()

        for agency in agencies:
            # Use AI for personalization if available, otherwise fallback
            try:
                prompt = (
                    f"Genera un messaggio di outreach WhatsApp di 2-3 frasi in italiano per l'agenzia '{agency['name']}' in {agency['address']}, {agency['city']}.\n"
                    f"Siamo un'azienda che fornisce un'AI che qualifica i lead notturni in 15 secondi.\n"
                    f"Il tono deve essere professionale ma amichevole. Non usare emoji."
                )
                message = container.ai.generate_response(prompt).strip().replace('"', "")
            except Exception:
                message = (
                    f"Ciao {agency['name']}! Abbiamo un'AI che qualifica i vostri lead notturni in 15 secondi su WhatsApp. "
                    f"Vi farebbe piacere vedere una breve demo per la vostra sede di {agency['city']}?"
                )

            row = {
                "name": agency["name"],
                "phone": agency["phone"],
                "address": agency["address"],
                "city": agency["city"],
                "outreach_message": message,
            }
            writer.writerow(row)

    print(f"✅ CSV Generated: {filename} ({len(agencies)} targets found)")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Find real estate agencies for B2B outreach.")
    parser.add_argument("--city", type=str, default="Milano", help="City to search in")
    parser.add_argument(
        "--output", type=str, default="outreach_targets.csv", help="Output CSV filename"
    )

    args = parser.parse_args()

    found_agencies = search_agencies(args.city)
    generate_outreach_csv(found_agencies, args.output)


if __name__ == "__main__":
    main()
