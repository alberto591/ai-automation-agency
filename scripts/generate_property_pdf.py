import argparse
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from infrastructure.adapters.mistral_adapter import MistralAdapter
from infrastructure.adapters.supabase_adapter import SupabaseAdapter
from infrastructure.ai_pdf_generator import PropertyPDFGenerator


def enrich_with_ai(property_data: dict, ai_adapter: MistralAdapter) -> dict:
    """Uses AI to fill missing fields from description."""
    fields_to_fix = [
        f
        for f in [
            "sqm",
            "rooms",
            "bathrooms",
            "energy_class",
            "floor",
            "has_terrace",
            "has_garden",
            "has_parking",
            "has_air_conditioning",
            "has_elevator",
            "condition",
            "heating_type",
        ]
        if property_data.get(f) is None or property_data.get(f) is False
    ]

    if not fields_to_fix:
        return property_data

    print(f"Enriching missing fields {fields_to_fix} using AI...")
    prompt = f"""
    Extract the following structured data from this Italian property description.
    Description: {property_data["description"]}

    Return a valid JSON object with these keys: {fields_to_fix}.
    - For booleans (has_*), use true or false.
    - For strings (condition, heating_type), use appropriate Italian terms (e.g., 'Ristrutturato', 'Autonomo').
    - For numbers (sqm, rooms), use integers.

    Only return the JSON.
    """
    try:
        response = ai_adapter.generate_response(prompt)
        import json
        import re

        # Clean response string to extract JSON
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            ai_data = json.loads(json_match.group(0))
            property_data.update(ai_data)
    except Exception as e:
        print(f"AI enrichment failed: {e}")

    return property_data


def main():
    parser = argparse.ArgumentParser(description="Generate a PDF brochure for an agency property.")
    parser.add_argument(
        "--index", type=int, default=0, help="Index of the property to use (from list)."
    )
    parser.add_argument(
        "--output", type=str, default="temp/property_brochure.pdf", help="Output file path."
    )
    parser.add_argument("--ai", action="store_true", help="Use AI to enrich missing fields.")
    parser.add_argument(
        "--save", action="store_true", help="Save AI-enriched data back to Supabase."
    )
    parser.add_argument(
        "--image", type=str, help="Force a specific image path/URL (useful for demos)."
    )

    args = parser.parse_args()

    print("Connecting to Supabase...")
    db = SupabaseAdapter()
    ai = MistralAdapter() if args.ai else None

    # Fetch properties
    properties = db.get_properties("", limit=10)

    if not properties:
        print("No properties found in database.")
        return

    if args.index >= len(properties):
        print(f"Index {args.index} out of range (found {len(properties)} properties).")
        return

    property_data = properties[args.index]

    if args.ai and ai:
        property_id = property_data.get("id")
        property_data = enrich_with_ai(property_data, ai)

        if args.save and property_id:
            print(f"Saving enriched data for property {property_id}...")
            # We only want to save the new fields extracted by AI
            # Filtering out internal fields if necessary, but update() is flexible
            fields_to_save = {
                k: v
                for k, v in property_data.items()
                if k
                in [
                    "sqm",
                    "rooms",
                    "bathrooms",
                    "energy_class",
                    "floor",
                    "has_terrace",
                    "has_garden",
                    "has_parking",
                    "has_air_conditioning",
                    "has_elevator",
                    "condition",
                    "heating_type",
                ]
            }
            try:
                db.update_property(property_id, fields_to_save)
                print("✅ Data saved to Supabase.")
            except Exception as e:
                print(f"❌ Failed to save data: {e}")

    # Apply manual image override if provided
    if args.image:
        print(f"🖼️  Using forced image: {args.image}")
        property_data["image_url"] = args.image

    print(f"Generating PDF for: {property_data.get('title')}...")

    gen = PropertyPDFGenerator()
    try:
        path = gen.generate_property_pdf(property_data, args.output)
        print(f"✅ Success! Brochure generated at: {path}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
