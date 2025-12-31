#!/usr/bin/env python3
"""
Generate mock historical transaction data for Fifi AI Appraisal training.

Creates realistic property transaction data for Italian real estate market
to populate the historical_transactions table for ML model training.
"""

import random
from datetime import datetime, timedelta
from pathlib import Path

# Property types and their characteristics
PROPERTY_ZONES = {
    "Florence-Centro": {"base_price_sqm": 5200, "variance": 0.15},
    "Florence-Rifredi": {"base_price_sqm": 3800, "variance": 0.12},
    "Florence-Campo di Marte": {"base_price_sqm": 4200, "variance": 0.13},
    "Prato-Centro": {"base_price_sqm": 2800, "variance": 0.10},
    "Lucca-Centro": {"base_price_sqm": 3200, "variance": 0.12},
}

CONDITIONS = ["excellent", "good", "fair", "needs_work", "luxury"]
CONDITION_MULTIPLIERS = {
    "excellent": 1.10,
    "good": 1.0,
    "fair": 0.90,
    "needs_work": 0.75,
    "luxury": 1.30,
}


def generate_transaction(zone: str, zone_data: dict) -> dict:
    """Generate a single realistic transaction."""
    # Random property size (focused on typical apartments)
    sqm = random.choice([45, 55, 65, 75, 85, 95, 105, 120, 140, 160])

    # Random condition
    condition = random.choices(
        CONDITIONS,
        weights=[15, 50, 20, 10, 5],  # Most are "good"
    )[0]

    # Calculate price with variance
    base_price = zone_data["base_price_sqm"]
    variance = random.uniform(-zone_data["variance"], zone_data["variance"])
    price_per_sqm = int(base_price * (1 + variance) * CONDITION_MULTIPLIERS[condition])
    sale_price = price_per_sqm * sqm

    # Random date in last 2 years
    days_ago = random.randint(0, 730)
    sale_date = datetime.now() - timedelta(days=days_ago)

    # Random features
    bedrooms = min(max(sqm // 30, 1), 4)  # Estimate based on size
    bathrooms = min(bedrooms, 2)
    floor = random.randint(0, 5)
    has_elevator = floor > 2 or random.random() > 0.6
    has_balcony = random.random() > 0.4

    return {
        "zone": zone,
        "city": zone.split("-")[0],
        "sqm": sqm,
        "sale_price_eur": sale_price,
        "price_per_sqm_eur": price_per_sqm,
        "condition": condition,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "floor": floor,
        "has_elevator": has_elevator,
        "has_balcony": has_balcony,
        "sale_date": sale_date.strftime("%Y-%m-%d"),
    }


def generate_mock_data(num_transactions: int = 500) -> list[dict]:
    """Generate mock transaction dataset."""
    transactions = []

    # Distribute across zones
    for zone, zone_data in PROPERTY_ZONES.items():
        zone_count = num_transactions // len(PROPERTY_ZONES)
        for _ in range(zone_count):
            transactions.append(generate_transaction(zone, zone_data))

    return transactions


def export_to_sql(transactions: list[dict], output_file: str):
    """Export transactions as SQL INSERT statements."""
    sql_lines = [
        "-- Mock Historical Transactions for Fifi AI Appraisal",
        f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"-- Total Records: {len(transactions)}",
        "",
        "INSERT INTO historical_transactions (",
        "    address, city, zone, sqm, sale_price_eur, price_per_sqm_eur,",
        "    bedrooms, bathrooms, floor, has_elevator, has_balcony,",
        "    condition, sale_date, source",
        ") VALUES",
    ]

    for i, tx in enumerate(transactions):
        comma = "," if i < len(transactions) - 1 else ";"
        address = f"{tx['zone']}, Via Example {random.randint(1, 100)}"

        sql_lines.append(
            f"    ('{address}', '{tx['city']}', '{tx['zone']}', {tx['sqm']}, "
            f"{tx['sale_price_eur']}, {tx['price_per_sqm_eur']}, "
            f"{tx['bedrooms']}, {tx['bathrooms']}, {tx['floor']}, "
            f"{tx['has_elevator']}, {tx['has_balcony']}, "
            f"'{tx['condition']}', '{tx['sale_date']}', 'Mock'){comma}"
        )

    return "\n".join(sql_lines)


if __name__ == "__main__":
    print("🏠 Generating mock transaction data...")

    # Generate data
    transactions = generate_mock_data(num_transactions=500)

    # Export to SQL
    output_path = Path(__file__).parent / "migrations" / "mock_data_insert.sql"
    sql_content = export_to_sql(transactions, str(output_path))

    with open(output_path, "w") as f:
        f.write(sql_content)

    print(f"✅ Generated {len(transactions)} mock transactions")
    print(f"📝 SQL file: {output_path}")

    # Print sample statistics
    avg_price = sum(tx["sale_price_eur"] for tx in transactions) / len(transactions)
    avg_sqm_price = sum(tx["price_per_sqm_eur"] for tx in transactions) / len(transactions)

    print("\n📊 Statistics:")
    print(f"   Average Sale Price: €{avg_price:,.0f}")
    print(f"   Average Price/sqm: €{avg_sqm_price:,.0f}")
    print(f"   Zones: {len(PROPERTY_ZONES)}")
    print("   Date Range: Last 2 years")
