import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from infrastructure.ai_pdf_generator import PropertyPDFGenerator

def test_single_pdf():
    gen = PropertyPDFGenerator(agency_name="Anzevino AI Real Estate", agency_color=(28, 40, 51))
    
    test_data = {
        "id": "prop_001",
        "title": "Villa di Lusso a Forte dei Marmi",
        "price": 2450000,
        "sqm": 350,
        "rooms": 8,
        "bathrooms": 4,
        "floor": 0,
        "energy_class": "A",
        "zone": "Vittoria Apuana",
        "image_url": "temp/hero_demo.png",
        "description": (
            "Esclusiva villa singola situata in una delle zone più prestigiose di Forte dei Marmi. "
            "La proprietà vanta un ampio giardino privato di 1000mq, una piscina riscaldata e finiture di altissimo pregio. "
            "Sviluppata su due livelli, offre ampi spazi luminosi, zona living open space, e suite padronale con cabina armadio. "
            "A soli 200 metri dal mare, rappresenta la soluzione ideale per chi cerca lusso e privacy."
        )
    }
    
    output_dir = "temp"
    output_file = os.path.join(output_dir, "villa_luxury.pdf")
    
    print(f"Generating PDF for: {test_data['title']}...")
    try:
        path = gen.generate_property_pdf(test_data, output_file)
        print(f"Success! PDF created at: {path}")
    except Exception as e:
        print(f"Error generating PDF: {e}")

if __name__ == "__main__":
    test_single_pdf()
