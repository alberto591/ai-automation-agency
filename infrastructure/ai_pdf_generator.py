import os
from datetime import datetime

from fpdf import FPDF

from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PropertyPDFGenerator:
    """Service to generate professional PDF brochures for properties."""

    def __init__(self, agency_name="Anzevino AI", agency_color=(44, 62, 80)):
        self.agency_name = agency_name
        self.agency_color = agency_color  # Default: Elegant Dark Blue/Grey

    def generate_property_pdf(self, property_data: dict, output_path: str) -> str:
        """
        Creates a PDF brochure from property data.

        Args:
            property_data: Dictionary containing title, price, description, sqm, rooms, etc.
            output_path: Where to save the generated PDF.

        Returns:
            The path to the generated PDF.
        """
        try:
            pdf = FPDF()
            pdf.add_page()

            # --- Header ---
            pdf.set_fill_color(*self.agency_color)
            pdf.rect(0, 0, 210, 40, "F")

            pdf.set_font("Helvetica", "B", 24)
            pdf.set_text_color(255, 255, 255)
            pdf.set_xy(10, 10)
            pdf.cell(0, 20, self.agency_name, ln=True)

            pdf.set_font("Helvetica", "", 12)
            pdf.set_xy(10, 25)
            pdf.cell(0, 10, "Scheda Immobiliare Professionale", ln=True)

            # --- Hero Image ---
            image_url = property_data.get("image_url")
            if image_url:
                try:
                    from tempfile import NamedTemporaryFile

                    import requests

                    # If it's a URL, download it
                    if image_url.startswith("http"):
                        resp = requests.get(image_url, timeout=10)
                        if resp.status_code == 200:
                            with NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                                tmp.write(resp.content)
                                temp_path = tmp.name
                            pdf.image(temp_path, x=10, y=45, w=190, h=100)
                            pdf.set_y(150)
                            # Clean up temp file
                            try:
                                os.unlink(temp_path)
                            except:
                                pass
                    else:
                        # Assume local path
                        pdf.image(image_url, x=10, y=45, w=190, h=100)
                        pdf.set_y(150)
                except Exception as img_err:
                    logger.warning("FAILED_TO_ADD_IMAGE_TO_PDF", context={"error": str(img_err)})
                    pdf.set_y(50)
            else:
                pdf.set_y(50)

            # --- Body ---
            pdf.set_text_color(0, 0, 0)
            # Y is already set above

            # Property Title
            pdf.set_font("Helvetica", "B", 20)
            pdf.multi_cell(0, 10, property_data.get("title", "Proprietà Senza Titolo"))
            pdf.ln(5)

            # Price Tag
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(*self.agency_color)
            price = property_data.get("price", 0)
            formatted_price = f"EUR {price:,.0f}".replace(",", ".")
            pdf.cell(0, 10, f"Prezzo: {formatted_price}", ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(10)

            # --- Features Table ---
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, "Dettagli Proprietà:", ln=True)
            pdf.set_font("Helvetica", "", 12)

            # Helper to handle None or missing values
            def format_val(val, suffix=""):
                if val is None or str(val).lower() == "none" or val == "":
                    return "Non specificato"
                return f"{val}{suffix}"

            # Columns: Feature | Value
            features = [
                ("Metri Quadrati", format_val(property_data.get("sqm"), " mq")),
                ("Locali", format_val(property_data.get("rooms"))),
                ("Bagni", format_val(property_data.get("bathrooms"))),
                ("Piano", format_val(property_data.get("floor"))),
                ("Classe Energetica", format_val(property_data.get("energy_class"))),
                ("Zona", format_val(property_data.get("zone"))),
                ("Terrazzo/Balcone", "Sì" if property_data.get("has_terrace") else "No"),
                ("Giardino", "Sì" if property_data.get("has_garden") else "No"),
                ("Parcheggio", "Sì" if property_data.get("has_parking") else "No"),
                ("Aria Condizionata", "Sì" if property_data.get("has_air_conditioning") else "No"),
                ("Ascensore", "Sì" if property_data.get("has_elevator") else "No"),
                ("Stato Immobile", format_val(property_data.get("condition"))),
                ("Riscaldamento", format_val(property_data.get("heating_type"))),
            ]

            for feature, value in features:
                pdf.set_font("Helvetica", "B", 11)
                pdf.cell(50, 8, f"{feature}:", border="B")
                pdf.set_font("Helvetica", "", 11)
                pdf.cell(0, 8, str(value), border="B", ln=True)

            pdf.ln(10)

            # --- Description ---
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, "Descrizione:", ln=True)
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(
                0, 7, property_data.get("description", "Nessuna descrizione disponibile.")
            )

            # --- Footer ---
            pdf.set_y(-30)
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(150, 150, 150)
            pdf.cell(0, 10, f"Generato il {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 0, "L")
            pdf.cell(0, 10, "Documento creato da Anzevino AI", 0, 0, "R")

            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            pdf.output(output_path)
            logger.info(
                "PDF_GENERATED", context={"path": output_path, "property": property_data.get("id")}
            )
            return output_path

        except Exception as e:
            logger.error("PDF_GENERATION_FAILED", context={"error": str(e)})
            raise


if __name__ == "__main__":
    # Test generation
    gen = PropertyPDFGenerator()
    test_data = {
        "id": "test-123",
        "title": "Attico Panoramico con Terrazza",
        "price": 850000,
        "sqm": 120,
        "rooms": 4,
        "bathrooms": 2,
        "floor": 5,
        "energy_class": "A+",
        "zone": "Centro Storico",
        "description": "Splendido attico situato nel cuore della città con vista mozzafiato. Finemente ristrutturato con materiali di pregio. Grande terrazzo vivibile e box auto incluso.",
    }
    gen.generate_property_pdf(test_data, "temp/test_property.pdf")
    print("PDF generated successfully at temp/test_property.pdf")
