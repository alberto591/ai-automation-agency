import os

import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    ),
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
}


def fetch_listing_page():
    url = "https://www.immobiliare.it/vendita-case/milano/"
    print(f"Fetching {url}...")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        print(f"Status Code: {resp.status_code}")

        if resp.status_code == 200:
            with open("temp/immobiliare_listing.html", "w", encoding="utf-8") as f:
                f.write(resp.text)
            print("✅ Saved HTML to temp/immobiliare_listing.html")
        else:
            print("❌ Failed to fetch page.")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    os.makedirs("temp", exist_ok=True)
    fetch_listing_page()
