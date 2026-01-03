#!/usr/bin/env python3
"""
Property Dataset Analysis Script
Analyzes the 243 properties collected from RapidAPI
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import statistics
from collections import Counter

from supabase import create_client

from config.settings import settings


def analyze_properties():
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    result = client.table("properties").select("*").execute()
    props = result.data

    print("📊 PROPERTY DATASET ANALYSIS")
    print(f"{'='*60}\n")
    print(f"Total Properties: {len(props)}\n")

    # Extract zones
    zones, cities = [], []
    for p in props:
        desc = p.get("description", "")
        if "ZONA:" in desc:
            zones.append(desc.split("ZONA:")[1].split(",")[0].strip())
        if "CITTÀ:" in desc:
            cities.append(desc.split("CITTÀ:")[1].split(".")[0].strip())

    print("📍 ZONE DISTRIBUTION:")
    for zone, count in Counter(zones).most_common():
        print(f"  {zone}: {count} ({count/len(props)*100:.1f}%)")

    print("\n🏙️ CITY DISTRIBUTION:")
    for city, count in Counter(cities).most_common():
        print(f"  {city}: {count} ({count/len(props)*100:.1f}%)")

    # Price analysis (filter None values)
    prices = []
    sqms = []
    for p in props:
        if p.get("price") and isinstance(p["price"], (int, float)) and p["price"] > 0:
            prices.append(p["price"])
        if p.get("sqm") and isinstance(p["sqm"], (int, float)) and p["sqm"] > 0:
            sqms.append(p["sqm"])

    if prices:
        print(f"\n💶 PRICE STATISTICS ({len(prices)} properties):")
        print(f"  Min: €{min(prices):,.0f}")
        print(f"  Max: €{max(prices):,.0f}")
        print(f"  Avg: €{statistics.mean(prices):,.0f}")
        print(f"  Median: €{statistics.median(prices):,.0f}")

    if sqms:
        print(f"\n📐 SIZE STATISTICS ({len(sqms)} properties):")
        print(f"  Min: {min(sqms)} sqm")
        print(f"  Max: {max(sqms)} sqm")
        print(f"  Avg: {statistics.mean(sqms):.0f} sqm")
        print(f"  Median: {statistics.median(sqms):.0f} sqm")

    # Price per sqm
    psqm = []
    for p in props:
        if (
            p.get("price")
            and p.get("sqm")
            and isinstance(p["price"], (int, float))
            and isinstance(p["sqm"], (int, float))
            and p["price"] > 0
            and p["sqm"] > 0
        ):
            psqm.append(p["price"] / p["sqm"])

    if psqm:
        print(f"\n💰 PRICE PER SQM ({len(psqm)} properties):")
        print(f"  Min: €{min(psqm):,.0f}/sqm")
        print(f"  Max: €{max(psqm):,.0f}/sqm")
        print(f"  Avg: €{statistics.mean(psqm):,.0f}/sqm")
        print(f"  Median: €{statistics.median(psqm):,.0f}/sqm")

    print("\n✅ DATA QUALITY:")
    complete = sum(1 for p in props if p.get("price", 0) > 0 and p.get("sqm", 0) > 0)
    with_images = sum(1 for p in props if p.get("image_url"))
    with_rooms = sum(1 for p in props if p.get("rooms", 0) > 0)
    print(f"  Complete (price + sqm): {complete}/{len(props)} ({complete/len(props)*100:.1f}%)")
    print(f"  With images: {with_images}/{len(props)} ({with_images/len(props)*100:.1f}%)")
    print(f"  With rooms data: {with_rooms}/{len(props)} ({with_rooms/len(props)*100:.1f}%)")

    # Price ranges
    if prices:
        ranges = {"<€200k": 0, "€200-400k": 0, "€400-600k": 0, "€600-1M": 0, ">€1M": 0}
        for p in prices:
            if p < 200000:
                ranges["<€200k"] += 1
            elif p < 400000:
                ranges["€200-400k"] += 1
            elif p < 600000:
                ranges["€400-600k"] += 1
            elif p < 1000000:
                ranges["€600-1M"] += 1
            else:
                ranges[">€1M"] += 1

        print("\n💵 PRICE DISTRIBUTION:")
        for range_name, count in ranges.items():
            if count > 0:
                print(f"  {range_name}: {count} ({count/len(prices)*100:.1f}%)")

    return props


if __name__ == "__main__":
    try:
        analyze_properties()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
