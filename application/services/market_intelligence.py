import json
from datetime import datetime, timedelta
from typing import Any

from domain.ports import AIPort, CachePort, DatabasePort
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class MarketIntelligenceService:
    def __init__(self, db: DatabasePort, ai: AIPort, cache: CachePort | None = None):
        self.db = db
        self.ai = ai
        self.cache = cache

    def get_market_analysis(self, city: str = "Milano", zone: str | None = None) -> dict[str, Any]:
        """
        Retrieves AI-generated market analysis, using cache if available.
        """
        cache_key = f"market_analysis:{city}:{zone or 'all'}"
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                try:
                    logger.info("MARKET_ANALYSIS_CACHE_HIT", context={"key": cache_key})
                    return json.loads(cached)  # type: ignore
                except Exception:
                    pass

        try:
            # 1. Fetch data from Supabase
            query = self.db.client.table("market_data").select("*").eq("city", city)  # type: ignore
            if zone:
                query = query.ilike("zone", f"%{zone}%")

            res = query.order("created_at", desc=True).limit(100).execute()
            data = res.data

            if not data:
                return {
                    "sentiment": "NEUTRAL",
                    "summary": "Dati insufficienti per generare un'analisi accurata.",
                    "stats": {"avg_price": 0, "count": 0},
                }

            # 2. Aggregate stats
            prices = [item["price_per_mq"] for item in data if item.get("price_per_mq")]
            avg_price = sum(prices) / len(prices) if prices else 0

            # 3. AI Analysis Prompt
            data_sample = data[:10]  # Sample for AI
            prompt = (
                f"Analizza i seguenti dati di mercato immobiliare per {city} {f'zona {zone}' if zone else ''}.\n"
                f"Dati: {json.dumps(data_sample)}\n"
                f"Prezzo medio calcolato: €{avg_price:.0f}/mq\n\n"
                f"Genera un'analisi in italiano che includa:\n"
                f"1. Sentiment di mercato (POSITIVO, NEUTRALE, NEGATIVO)\n"
                f"2. Un breve riassunto delle tendenze attuali\n"
                f"3. Un consiglio per gli investitori\n\n"
                f"Output JSON: {{'sentiment': '...', 'summary': '...', 'investor_tip': '...'}}"
            )

            ai_res = self.ai.generate_response(prompt)
            clean_res = ai_res.replace("```json", "").replace("```", "").strip()

            try:
                analysis = json.loads(clean_res)
            except (json.JSONDecodeError, ValueError):
                analysis = {
                    "sentiment": "NEUTRAL",
                    "summary": ai_res,
                    "investor_tip": "Consultare un esperto locale.",
                }

            analysis["stats"] = {
                "avg_price": round(avg_price, 2),
                "count": len(data),
                "min_price": round(min(prices), 2) if prices else 0,
                "max_price": round(max(prices), 2) if prices else 0,
            }

            # Cache the result for 24 hours
            if self.cache:
                self.cache.set(cache_key, json.dumps(analysis), ttl=86400)

            return analysis  # type: ignore

        except Exception as e:
            logger.error("MARKET_ANALYSIS_FAILED", context={"city": city, "error": str(e)})
            return {"error": "Failed to generate market analysis"}

    def predict_market_trend(self, zone: str, city: str = "Milano") -> dict[str, Any]:
        """
        Simple predictive logic based on recent data vs older data.
        """
        try:
            # Fetch last 30 days vs previous 30 days
            now = datetime.now()
            thirty_days_ago = (now - timedelta(days=30)).isoformat()
            sixty_days_ago = (now - timedelta(days=60)).isoformat()

            # Recent
            res_recent = (
                self.db.client.table("market_data")  # type: ignore
                .select("price_per_mq")
                .eq("city", city)
                .ilike("zone", f"%{zone}%")
                .gte("created_at", thirty_days_ago)
                .execute()
            )

            # Historical
            res_history = (
                self.db.client.table("market_data")  # type: ignore
                .select("price_per_mq")
                .eq("city", city)
                .ilike("zone", f"%{zone}%")
                .gte("created_at", sixty_days_ago)
                .lt("created_at", thirty_days_ago)
                .execute()
            )

            recent_prices = [r["price_per_mq"] for r in res_recent.data if r.get("price_per_mq")]
            history_prices = [r["price_per_mq"] for r in res_history.data if r.get("price_per_mq")]

            avg_recent = sum(recent_prices) / len(recent_prices) if recent_prices else 0
            avg_history = sum(history_prices) / len(history_prices) if history_prices else 0

            trend = "STABLE"
            change_pct = 0
            if avg_history > 0:
                change_pct = (avg_recent - avg_history) / avg_history
                if change_pct > 0.02:
                    trend = "RISING"
                elif change_pct < -0.02:
                    trend = "FALLING"

            return {
                "zone": zone,
                "trend": trend,
                "change_pct": round(change_pct * 100, 2),
                "avg_recent": round(avg_recent, 2),
                "avg_historical": round(avg_history, 2),
            }

        except Exception as e:
            logger.error("TREND_PREDICTION_FAILED", context={"zone": zone, "error": str(e)})
            return {"error": "Failed to predict trend"}
