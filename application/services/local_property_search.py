"""
Local Property Search Service
Provides low-latency appraisal data by querying local Supabase database.
"""

from typing import Any, cast

from supabase import Client

from domain.appraisal import Comparable
from infrastructure.logging import get_logger

logger = get_logger(__name__)

# Constants for maintainability
SIZE_RANGE_BUFFER = 0.20  # +/- 20% on square meters
MAX_RESULTS_LIMIT = 10
MIN_PRICE_PER_SQM = 500
MAX_PRICE_PER_SQM = 15000
TITLE_MAX_LENGTH = 100
DESC_MAX_LENGTH = 300

# City Normalization Mapping
CITY_VARIANTS = {
    "florence": "Firenze",
    "firenze": "Firenze",
    "siena": "Siena",
    "pisa": "Pisa",
    "lucca": "Lucca",
    "arezzo": "Arezzo",
    "grosseto": "Grosseto",
    "livorno": "Livorno",
    "milan": "Milano",
    "milano": "Milano",
    "rome": "Roma",
    "roma": "Roma",
    "naples": "Napoli",
    "napoli": "Napoli",
    "venice": "Venezia",
    "venezia": "Venezia",
}


class LocalPropertySearchService:
    """Service to search for comparable properties in the local database."""

    def __init__(self, db_client: Client):
        self.db = db_client

    def search_local_comparables(
        self,
        city: str,
        zone: str | None = None,
        property_type: str | None = None,
        surface_sqm: int | None = None,
        min_comparables: int = 3,
    ) -> list[Comparable]:
        """
        Search for properties in the local database.
        """
        try:
            # 1. Normalize City Name
            normalized_city = CITY_VARIANTS.get(city.lower(), city)

            # 2. Build Query
            query = self.db.table("properties").select("*").eq("status", "available")

            if normalized_city:
                query = query.ilike("description", f"%{normalized_city}%")

            if zone:
                query = query.ilike("description", f"%{zone}%")

            if property_type:
                # Basic mapping for property types if needed
                query = query.ilike("title", f"%{property_type}%")

            if surface_sqm:
                min_sqm = int(surface_sqm * (1 - SIZE_RANGE_BUFFER))
                max_sqm = int(surface_sqm * (1 + SIZE_RANGE_BUFFER))
                query = query.gte("sqm", min_sqm).lte("sqm", max_sqm)

            # 3. Execute Search
            result = query.limit(MAX_RESULTS_LIMIT).execute()

            properties = result.data
            if not properties or not isinstance(properties, list):
                logger.info("LOCAL_SEARCH_NO_RESULTS")
                return []

            # 4. Filter and Transform
            comparables = []
            for prop_data in properties:
                prop = cast(dict[str, Any], prop_data)
                try:
                    price = prop.get("price")
                    sqm = prop.get("sqm")

                    if price and sqm and sqm > 0:
                        price_per_sqm = float(price) / float(sqm)

                        if MIN_PRICE_PER_SQM < price_per_sqm < MAX_PRICE_PER_SQM:
                            comparables.append(
                                Comparable(
                                    title=cast(str, prop.get("title", "Property"))[
                                        :TITLE_MAX_LENGTH
                                    ],
                                    price=float(price),
                                    surface_sqm=int(sqm),
                                    price_per_sqm=round(price_per_sqm, 0),
                                    description=cast(str, prop.get("description", ""))[
                                        :DESC_MAX_LENGTH
                                    ],
                                )
                            )
                except (KeyError, ValueError, TypeError) as e:
                    logger.debug(f"Skipping invalid property: {e}")
                    continue

            logger.info(
                "LOCAL_SEARCH_COMPLETE",
                context={
                    "found": len(comparables),
                    "city": normalized_city,
                    "zone": zone,
                },
            )

            return comparables

        except Exception as e:
            logger.error("LOCAL_SEARCH_ERROR", context={"error": str(e)})
            return []
