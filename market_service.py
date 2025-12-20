import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "idealista2.p.rapidapi.com"

# Expert Fallbacks for Tuscany (November 2025 Market Trends)
# Used if API is disconnected or key is missing.
TUSCANY_EXPERT_DATA = {
    "FIRENZE": 4546,
    "SIENA": 3100,
    "PISA": 2500,
    "LUCCA": 3544,
    "AREZZO": 1524,
    "LIVORNO": 2100,
    "GROSSETO": 2500,
    "PRATO": 2200,
    "PISTOIA": 2100,
    "MASSA": 2400,
    "CARRARA": 1800,
    "FORTE DEI MARMI": 10500,
    "VIAREGGIO": 3400,
    "MONTE ARGENTARIO": 5500,
    "FIGLINE E INCISA VALDARNO": 2400,
    "FIGLINE": 2400,
    "INCISA VALDARNO": 2300,
    "TOSCANA": 2594
}

def get_live_market_price(zone, city=""):
    """
    Fetches live market data from Idealista via RapidAPI.
    Note: Requires an active RapidAPI Key. 
    """
    zone_upper = zone.upper()
    
    # 1. Check for Tuscany Expert Match first if no API Key
    if not RAPIDAPI_KEY:
        for t_zone, t_price in TUSCANY_EXPERT_DATA.items():
            if t_zone in zone_upper:
                logger.info(f"📍 Tuscany Expert Data used for {zone}: €{t_price}/mq")
                return t_price
        logger.warning("⚠️ RAPIDAPI_KEY not found. Skipping live market data lookup.")
        return None

    url = f"https://{RAPIDAPI_HOST}/properties/list"
    
    # We search for properties in the zone to calculate an average
    # This is a robust way to get 'live' data without a direct 'avg' endpoint
    params = {
        "locationName": f"{zone}, {city}".strip(", "),
        "operation": "sale",
        "propertyType": "homes",
        "country": "it",
        "maxItems": "20"
    }

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    # 1. Resolve Location ID via Autocomplete
    location_id = None
    try:
        ac_url = f"https://{RAPIDAPI_HOST}/auto-complete"
        ac_params = {"prefix": zone, "country": "it"}
        ac_resp = requests.get(ac_url, headers=headers, params=ac_params, timeout=10)
        if ac_resp.status_code == 200:
            ac_data = ac_resp.json()
            locations = ac_data.get("locations", [])
            if locations:
                # Prioritize 'neighborhood' or 'municipality' if available
                location_id = locations[0].get("locationId")
                logger.info(f"📍 Resolved location '{zone}' to ID: {location_id}")
    except Exception as e:
        logger.warning(f"⚠️ Autocomplete failed for {zone}: {e}")

    # 2. Search Properties
    url = f"https://{RAPIDAPI_HOST}/properties/list"
    params = {
        "operation": "sale",
        "propertyType": "homes",
        "country": "it",
        "maxItems": "20"
    }
    
    if location_id:
        params["locationId"] = location_id
    else:
        params["locationName"] = f"{zone}, {city}".strip(", ")

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code != 200:
            logger.error(f"❌ RapidAPI Error {response.status_code}: {response.text}")
            return None
            
        data = response.json()
        properties = data.get("elementList", [])
        if not properties:
            logger.warning(f"⚠️ No properties found for {zone}")
            return None
            
        prices_mq = []
        for p in properties:
            # Skip auctions as they skew the price average downwards
            if p.get("isAuction"):
                continue
                
            price = p.get("price")
            size = p.get("size")
            if price and size and size > 0:
                val = price / size
                # Filter out obvious outliers (auctions not caught by flag, or luxury)
                if 800 < val < 20000:
                    prices_mq.append(val)
        
        if not prices_mq:
            logger.warning(f"⚠️ All property data for {zone} was filtered out as outliers.")
            return None
            
        avg_price = sum(prices_mq) / len(prices_mq)
        logger.info(f"🌐 Live API Data for {zone}: €{int(avg_price)}/mq (from {len(prices_mq)} properties)")
        return int(avg_price)
        
    except Exception as e:
        logger.error(f"❌ RapidAPI Market Data error: {e}")
        return None
