"""Generate synthetic real estate transaction data for XGBoost training.

This script creates realistic transaction records that mimic OMI (Osservatorio del Mercato Immobiliare)
data structure. Used as a fallback until real historical data is acquired.

Usage:
    python scripts/data/generate_synthetic_data.py --n_samples 50000 --output data/synthetic_transactions.csv
"""

import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from infrastructure.logging import get_logger

logger = get_logger(__name__)


class SyntheticDataGenerator:
    """Generates realistic synthetic real estate transactions for training."""

    # Zone-based pricing (€/sqm) - Based on Italian market knowledge
    ZONE_PRICING = {
        # Florence
        "duomo-firenze": 6500,
        "santa-croce-firenze": 5800,
        "oltrarno-firenze": 5200,
        "rifredi-firenze": 3800,
        "novoli-firenze": 3500,
        # Milan
        "centro-milano": 8000,
        "brera-milano": 7500,
        "navigli-milano": 6500,
        "porta-romana-milano": 5500,
        "lambrate-milano": 4000,
        # Rome
        "centro-storico-roma": 7000,
        "trastevere-roma": 6200,
        "prati-roma": 5800,
        "testaccio-roma": 5000,
        "san-lorenzo-roma": 4200,
        # Other cities
        "centro-bologna": 4500,
        "centro-pisa": 3800,
        "centro-lucca": 3200,
    }

    CONDITION_MULTIPLIERS = {
        "luxury": 1.4,
        "excellent": 1.2,
        "good": 1.0,
        "fair": 0.85,
        "poor": 0.65,
    }

    CADASTRAL_CATEGORIES = ["A/2", "A/3", "A/4", "A/7"]  # Typical residential

    def __init__(self, seed: int = 42):
        """Initialize generator with random seed for reproducibility."""
        random.seed(seed)
        np.random.seed(seed)
        logger.info("SYNTHETIC_DATA_GENERATOR_INIT", context={"seed": seed})

    def generate_transactions(self, n_samples: int = 50000) -> pd.DataFrame:
        """Generate synthetic transaction dataset.

        Args:
            n_samples: Number of transactions to generate

        Returns:
            DataFrame with columns matching historical_transactions schema
        """
        logger.info("GENERATING_SYNTHETIC_DATA", context={"n_samples": n_samples})

        transactions = []
        zones = list(self.ZONE_PRICING.keys())

        # Generate transactions over past 3 years
        end_date = datetime.now()
        start_date = end_date - timedelta(days=3 * 365)

        for i in range(n_samples):
            zone = random.choice(zones)
            base_price_sqm = self.ZONE_PRICING[zone]

            # Property characteristics
            sqm = int(np.random.normal(85, 25))  # Mean 85sqm, std 25
            sqm = max(30, min(sqm, 250))  # Clamp to realistic range

            bedrooms = self._infer_bedrooms(sqm)
            bathrooms = min(bedrooms, random.randint(1, 3))
            floor = random.randint(0, 6)
            has_elevator = floor > 2 and random.random() > 0.3
            has_balcony = random.random() > 0.4
            has_garden = floor == 0 and random.random() > 0.8
            condition = random.choices(
                list(self.CONDITION_MULTIPLIERS.keys()),
                weights=[0.05, 0.25, 0.45, 0.20, 0.05],  # Normal distribution
            )[0]

            # Calculate sale price
            condition_mult = self.CONDITION_MULTIPLIERS[condition]
            floor_mult = 1.0 + (floor * 0.02)  # Higher floors slightly more expensive
            elevator_mult = 1.05 if has_elevator else 1.0
            balcony_mult = 1.03 if has_balcony else 1.0
            garden_mult = 1.15 if has_garden else 1.0

            price_sqm = (
                base_price_sqm
                * condition_mult
                * floor_mult
                * elevator_mult
                * balcony_mult
                * garden_mult
            )

            # Add Gaussian noise (±10-15% variance)
            noise_factor = np.random.normal(1.0, 0.12)
            price_sqm *= noise_factor

            sale_price = int(sqm * price_sqm)

            # Generate random transaction date
            days_ago = random.randint(0, (end_date - start_date).days)
            sale_date = end_date - timedelta(days=days_ago)

            # Create transaction record
            transaction = {
                "zone_slug": zone,
                "city": zone.split("-")[-1].capitalize(),
                "address": f"Via {random.choice(['Roma', 'Venezia', 'Dante', 'Mazzini'])} {random.randint(1, 150)}",
                "sale_date": sale_date.strftime("%Y-%m-%d"),
                "sale_price_eur": sale_price,
                "sqm": sqm,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "floor": floor,
                "has_elevator": has_elevator,
                "has_balcony": has_balcony,
                "has_garden": has_garden,
                "condition": condition,
                "energy_class": random.choice(["A", "B", "C", "D", "E", "F", "G"]),
                "property_age_years": random.randint(5, 80),
                "cadastral_category": random.choice(self.CADASTRAL_CATEGORIES),
                "latitude": self._fake_lat(zone),
                "longitude": self._fake_lng(zone),
            }

            transactions.append(transaction)

            if (i + 1) % 10000 == 0:
                logger.info("GENERATION_PROGRESS", context={"generated": i + 1, "total": n_samples})

        df = pd.DataFrame(transactions)
        logger.info("SYNTHETIC_DATA_COMPLETE", context={"shape": df.shape})
        return df

    def _infer_bedrooms(self, sqm: int) -> int:
        """Infer realistic bedroom count from sqm."""
        if sqm < 50:
            return 1
        elif sqm < 70:
            return 2
        elif sqm < 100:
            return random.choice([2, 3])
        elif sqm < 140:
            return random.choice([3, 4])
        else:
            return random.choice([4, 5])

    def _fake_lat(self, zone: str) -> float:
        """Generate fake latitude based on zone."""
        city = zone.split("-")[-1]
        base_coords = {
            "firenze": 43.77,
            "milano": 45.46,
            "roma": 41.90,
            "bologna": 44.49,
            "pisa": 43.72,
            "lucca": 43.84,
        }
        base = base_coords.get(city, 43.77)
        return round(base + np.random.uniform(-0.05, 0.05), 6)

    def _fake_lng(self, zone: str) -> float:
        """Generate fake longitude based on zone."""
        city = zone.split("-")[-1]
        base_coords = {
            "firenze": 11.25,
            "milano": 9.19,
            "roma": 12.50,
            "bologna": 11.34,
            "pisa": 10.40,
            "lucca": 10.50,
        }
        base = base_coords.get(city, 11.25)
        return round(base + np.random.uniform(-0.05, 0.05), 6)


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic transaction data for XGBoost training"
    )
    parser.add_argument(
        "--n_samples", type=int, default=50000, help="Number of transactions to generate"
    )
    parser.add_argument(
        "--output", type=str, default="data/synthetic_transactions.csv", help="Output CSV path"
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")

    args = parser.parse_args()

    # Create output directory
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate data
    generator = SyntheticDataGenerator(seed=args.seed)
    df = generator.generate_transactions(n_samples=args.n_samples)

    # Save to CSV
    df.to_csv(output_path, index=False)
    logger.info("SYNTHETIC_DATA_SAVED", context={"path": str(output_path), "rows": len(df)})

    # Print summary statistics
    print("\n" + "=" * 60)
    print("SYNTHETIC DATA GENERATION COMPLETE")
    print("=" * 60)
    print(f"Total Transactions: {len(df):,}")
    print(f"Output Path: {output_path}")
    print("\nPrice Statistics:")
    print(f"  Mean: €{df['sale_price_eur'].mean():,.0f}")
    print(f"  Median: €{df['sale_price_eur'].median():,.0f}")
    print(f"  Min: €{df['sale_price_eur'].min():,.0f}")
    print(f"  Max: €{df['sale_price_eur'].max():,.0f}")
    print("\nZone Distribution:")
    print(df["zone_slug"].value_counts().head(10))
    print("=" * 60)


if __name__ == "__main__":
    main()
