"""
Local Property Search Service
Searches Supabase properties database before falling back to Perplexity API
"""

from supabase import Client

from domain.appraisal import Comparable
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class LocalPropertySearchService:
    """Search local Supabase database for property comparables."""

    def __init__(self, db_client: Client):
        self.db = db_client

    def search_local_comparables(
        self,
        city: str,
        zone: str,
        property_type: str,
        surface_sqm: int,
        min_comparables: int = 3,
    ) -> list[Comparable]:
        """
        Search local database for property comparables.

        Args:
            city: City name (e.g., "Milano", "Firenze")
            zone: Zone/neighborhood (e.g., "Centro", "Navigli")
            property_type: Type of property (e.g., "apartment", "villa")
            surface_sqm: Target property size
            min_comparables: Minimum number of comparables to return

        Returns:
            List of Comparable objects if sufficient matches found, empty list otherwise
        """
        try:
            # Define size range (±30% of target size)
            size_min = int(surface_sqm * 0.7)
            size_max = int(surface_sqm * 1.3)

            logger.info(
                "LOCAL_SEARCH_START",
                context={
                    "city": city,
                    "zone": zone,
                    "size_range": f"{size_min}-{size_max}",
                },
            )

            # Query properties matching criteria
            # Search description field for zone/city since they're embedded in text
            query = self.db.table("properties").select("*")

            # Filter by description containing city and zone
            zone_pattern = f"%{zone}%"
            city_pattern = f"%{city}%"

            result = (
                query.ilike("description", zone_pattern)
                .ilike("description", city_pattern)
                .gte("sqm", size_min)
                .lte("sqm", size_max)
                .gt("price", 10000)  # Exclude obviously invalid prices
                .limit(10)  # Get top 10 matches
                .execute()
            )

            properties = result.data

            if not properties:
                logger.info("LOCAL_SEARCH_NO_RESULTS")
                return []

            # Convert to Comparable objects
            comparables = []
            for prop in properties:
                try:
                    if prop.get("price") and prop.get("sqm") and prop["sqm"] > 0:
                        price_per_sqm = prop["price"] / prop["sqm"]

                        # Sanity check: €500-€15000/sqm
                        if 500 < price_per_sqm < 15000:
                            comparables.append(
                                Comparable(
                                    title=prop.get("title", "Property")[:100],
                                    price=float(prop["price"]),
                                    surface_sqm=int(prop["sqm"]),
                                    price_per_sqm=round(price_per_sqm, 0),
                                    description=prop.get("description", "")[:200],
                                )
                            )
                except (KeyError, ValueError, TypeError) as e:
                    logger.debug(f"Skipping invalid property: {e}")
                    continue

            logger.info(
                "LOCAL_SEARCH_COMPLETE",
                context={
                    "found": len(comparables),
                    "required": min_comparables,
                },
            )

            # Only return if we have enough comparables
            if len(comparables) >= min_comparables:
                return comparables[:min_comparables]  # Return only what's needed
            else:
                return []  # Not enough, caller should fall back to Perplexity

        except Exception as e:
            logger.error(
                "LOCAL_SEARCH_ERROR",
                context={"error": str(e)},
                exc_info=True,
            )
            return []  # Fall back to Perplexity on error
