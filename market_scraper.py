import requests
from bs4 import BeautifulSoup
import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv
import re

load_dotenv()

# Initialize Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
}

def scrape_immobiliare(url):
    """
    Extracts property details from Immobiliare.it
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to reach Immobiliare.it: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Price
        price_tag = soup.find('div', class_='nd-list__item nd-list__item--main nd-list__item--price') or \
                    soup.find('li', class_='nd-list__item nd-list__item--main nd-list__item--price')
        price_text = price_tag.get_text() if price_tag else "0"
        price = float(re.sub(r'[^\d]', '', price_text)) if price_text else 0
        
        # 2. SQM
        sqm_tag = soup.find('li', aria_label='superficie')
        sqm_text = sqm_tag.get_text() if sqm_tag else "0"
        sqm = float(re.sub(r'[^\d]', '', sqm_text)) if sqm_text else 0
        
        # 3. Rooms
        rooms_tag = soup.find('li', aria_label='locali')
        rooms_text = rooms_tag.get_text() if rooms_tag else "0"
        rooms = int(re.sub(r'[^\d]', '', rooms_text)) if rooms_text else 0

        # 4. Bathrooms
        bathrooms_tag = soup.find('li', aria_label='bagni')
        bathrooms_text = bathrooms_tag.get_text() if bathrooms_tag else "0"
        bathrooms = int(re.sub(r'[^\d]', '', bathrooms_text)) if bathrooms_text else 0

        # 5. Floor
        floor_tag = soup.find('li', aria_label='piano')
        floor_text = floor_tag.get_text() if floor_tag else "0"
        # Handle 'Terra', 'Rialzato', etc.
        floor = 0
        if 'T' in floor_text or 'terra' in floor_text.lower():
            floor = 0
        elif re.search(r'\d+', floor_text):
            floor = int(re.search(r'\d+', floor_text).group())

        # 6. Energy Class
        energy_tag = soup.find('span', class_='nd-list__item nd-list__item--main nd-list__item--energy')
        energy_class = energy_tag.get_text().strip() if energy_tag else "N/A"

        # 7. Title/Description
        title_tag = soup.find('h1', class_='nd-title')
        title = title_tag.get_text() if title_tag else "Appartamento"
        
        # 8. Zone
        zone_tag = soup.find('span', class_='nd-title__sub-title')
        zone = zone_tag.get_text() if zone_tag else "Milano"

        price_per_mq = round(price / sqm, 2) if sqm > 0 else 0

        data = {
            "portal_url": url,
            "title": title,
            "price": price,
            "sqm": sqm,
            "rooms": rooms,
            "bathrooms": bathrooms,
            "floor": floor,
            "energy_class": energy_class,
            "price_per_mq": price_per_mq,
            "zone": zone,
            "city": "Milano"
        }
        
        return data

    except Exception as e:
        print(f"⚠️ Scraper Error (Immobiliare): {e}")
        return None

def save_to_market_data(data):
    """
    Saves the extracted data to Supabase market_data table
    """
    if not data:
        return
    
    try:
        # Upsert based on portal_url
        result = supabase.table("market_data").upsert(data, on_conflict="portal_url").execute()
        print(f"✅ Market Data Saved/Updated: {data['title']} in {data['zone']}")
        return result
    except Exception as e:
        print(f"❌ Supabase Error: {e}")
        # If table doesn't exist, provide a hint
        if "relation \"market_data\" does not exist" in str(e):
            print("💡 TIP: Run the SQL migration in docs/market-data-migration.sql first!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
        print(f"🔍 Scraping: {target_url}")
        property_data = scrape_immobiliare(target_url)
        if property_data:
            print(json.dumps(property_data, indent=2))
            save_to_market_data(property_data)
        else:
            print("❌ No data extracted.")
    else:
        print("Usage: python3 market_scraper.py <URL>")
