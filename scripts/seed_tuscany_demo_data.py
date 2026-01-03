"""
Seed high-quality Tuscany demo data for the appraisal tool.
Focuses on Firenze, Siena, and Chianti to ensure the demo is spectacular even without active scraping.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase import create_client

from config.settings import settings
from infrastructure.logging import get_logger

logger = get_logger(__name__)

DEMO_PROPERTIES = [
    # === FIRENZE CENTRO ===
    {
        "title": "Attico Prestigioso vista Duomo",
        "description": "📍 ZONA: Centro, CITTÀ: Firenze. Rarissimo attico di 150mq con terrazza abitabile di 40mq affacciata direttamente sulla Cupola del Brunelleschi. Finiture di lusso, 3 camere, 2 bagni, aria condizionata e ascensore.",
        "price": 1850000,
        "sqm": 150,
        "city": "Firenze",
        "zone": "Centro",
        "image_url": "https://images.unsplash.com/photo-1541310592956-e3d9461dfbf3?auto=format&fit=crop&w=800&q=80",
    },
    {
        "title": "Appartamento Elegante in Palazzo Storico",
        "description": "📍 ZONA: Centro, CITTÀ: Firenze. Situato in un palazzo del XVI secolo vicino a Piazza della Signoria. 90mq finemente ristrutturati, soffitti a cassettoni, 2 camere matrimoniali, cucina moderna.",
        "price": 720000,
        "sqm": 90,
        "city": "Firenze",
        "zone": "Centro",
        "image_url": "https://images.unsplash.com/photo-1513584684374-8bdb7489feef?auto=format&fit=crop&w=800&q=80",
    },
    {
        "title": "Loft Industrial Lungarno",
        "description": "📍 ZONA: Oltrarno, CITTÀ: Firenze. Spazioso loft di 120mq ristrutturato in stile contemporaneo. Soffitti alti, grandi finestre, vista Arno, 1 camera open space, 2 bagni.",
        "price": 850000,
        "sqm": 120,
        "city": "Firenze",
        "zone": "Oltrarno",
        "image_url": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80",
    },
    # === SIENA ===
    {
        "title": "Residenza Storica afacciata su Piazza del Campo",
        "description": "📍 ZONA: Centro Storico, CITTÀ: Siena. Unico nel suo genere, appartamento di 110mq con 3 finestre direttamente sulla Piazza del Campo. Soffitti affrescati, 2 camere, ampio salone.",
        "price": 980000,
        "sqm": 110,
        "city": "Siena",
        "zone": "Centro Storico",
        "image_url": "https://images.unsplash.com/photo-1534430480872-3498386e7a55?auto=format&fit=crop&w=800&q=80",
    },
    {
        "title": "Trilocale Ristrutturato Porta Camollia",
        "description": "📍 ZONA: Centro Storico, CITTÀ: Siena. Luminoso appartamento di 75mq al secondo piano. Recentemente ristrutturato, travi a vista, 2 camere, climatizzato.",
        "price": 340000,
        "sqm": 75,
        "city": "Siena",
        "zone": "Centro Storico",
        "image_url": "https://images.unsplash.com/photo-1493809842364-78817add7ffb?auto=format&fit=crop&w=800&q=80",
    },
    # === CHIANTI ===
    {
        "title": "Casale Toscano con Uliveto e Piscina",
        "description": "📍 ZONA: Greve, CITTÀ: Chianti. Splendido casale in pietra di 250mq immerso nel verde. Terreno di 2 ettari con uliveto, piscina privata, 4 camere, porticato panoramico.",
        "price": 1250000,
        "sqm": 250,
        "city": "Chianti",
        "zone": "Greve",
        "image_url": "https://images.unsplash.com/photo-1523217582562-09d0def993a6?auto=format&fit=crop&w=800&q=80",
    },
    {
        "title": "Villa Moderna tra i vigneti",
        "description": "📍 ZONA: Castellina, CITTÀ: Chianti. Nuova costruzione in classe A4. 180mq su un unico livello, ampie vetrate, vista mozzafiato sui vigneti, domotica, piscina a sfioro.",
        "price": 1450000,
        "sqm": 180,
        "city": "Chianti",
        "zone": "Castellina",
        "image_url": "https://images.unsplash.com/photo-1613490493576-7fde63acd811?auto=format&fit=crop&w=800&q=80",
    },
    # === PISA & LUCCA ===
    {
        "title": "Appartamento con vista Torre",
        "description": "📍 ZONA: Centro, CITTÀ: Pisa. Elegante trilocale di 85mq a pochi passi dalla Torre Pendente. Ottimo investimento per affitti turistici, 2 camere, aria condizionata.",
        "price": 410000,
        "sqm": 85,
        "city": "Pisa",
        "zone": "Centro",
        "image_url": "https://images.unsplash.com/photo-1516483642144-738b655b48b6?auto=format&fit=crop&w=800&q=80",
    },
    {
        "title": "Ddimora Signorile entro le Mura",
        "description": "📍 ZONA: Centro Storico, CITTÀ: Lucca. Prestigioso appartamento di 200mq situato in uno dei palazzi più belli di Lucca. Salone di 60mq, caminetto originale, 3 ampie camere.",
        "price": 950000,
        "sqm": 200,
        "city": "Lucca",
        "zone": "Centro Storico",
        "image_url": "https://images.unsplash.com/photo-1560185127-6ed189bf02f4?auto=format&fit=crop&w=800&q=80",
    },
]


def seed_demo_data():
    """Seed the database with high-quality Tuscany demo properties."""
    key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY
    client = create_client(settings.SUPABASE_URL, key)

    print(f"🚀 Seeding {len(DEMO_PROPERTIES)} premium Tuscany properties...")

    count = 0
    for prop in DEMO_PROPERTIES:
        try:
            # Add price_per_mq
            prop["price_per_mq"] = prop["price"] / prop["sqm"]

            # Check if already exists by title
            res = client.table("properties").select("id").eq("title", prop["title"]).execute()
            if res.data:
                print(f"  ⏭️ Skipping existing: {prop['title']}")
                continue

            client.table("properties").insert(prop).execute()
            print(f"  ✅ Inserted: {prop['title']} ({prop['city']}, {prop['zone']})")
            count += 1
        except Exception as e:
            print(f"  ❌ Error inserting {prop['title']}: {e}")

    print(f"\n✨ Seeding complete. Added {count} new properties.")


if __name__ == "__main__":
    seed_demo_data()
