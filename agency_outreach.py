import csv

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def search_agencies(city="Milano", pages=1):
    """
    Simulates finding real estate agencies.
    In a real scenario, this would use Google Maps API or a targeted scraper.
    """
    print(f"🚀 Searching for Real Estate Agencies in {city}...")

    # Example logic for a yellow-pages style search
    # This is a template. For production, use Google Places API.
    agencies = []

    # Mocked data for demonstration if scraper fails
    mock_data = [
        {
            "name": "Milano Elite Properties",
            "phone": "+393401111111",
            "address": "Via Dante 10",
            "city": city,
        },
        {
            "name": "Vivere Meglio Real Estate",
            "phone": "+393402222222",
            "address": "Piazza Duomo 5",
            "city": city,
        },
        {
            "name": "Global House Milano",
            "phone": "+393403333333",
            "address": "Corso Buenos Aires 12",
            "city": city,
        },
    ]

    # For now, we return mock data + any results found
    # (Scraper logic would go here)

    return mock_data


def generate_outreach_csv(agencies, filename="outreach_targets.csv"):
    """
    Saves agencies to a CSV with suggested outreach messages.
    """
    keys = ["name", "phone", "address", "city", "outreach_message"]

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()

        for agency in agencies:
            # Personalize the message
            message = (
                f"Ciao {agency['name']}! Ho visto la vostra vetrina in {agency['address']}. "
                f"Ricevete lead notturni? La nostra AI li qualifica in 15 secondi su WhatsApp. "
                f"Vuoi vedere una demo?"
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


def main():
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
