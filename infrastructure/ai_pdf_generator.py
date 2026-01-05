import os
from datetime import datetime
from typing import Any

from fpdf import FPDF  # fpdf2 package
from fpdf.enums import XPos, YPos

from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PropertyPDFGenerator:
    """Service to generate professional PDF brochures for properties."""

    def __init__(
        self, agency_name: str = "Anzevino AI", agency_color: tuple[int, int, int] = (44, 62, 80)
    ) -> None:
        self.agency_name = agency_name
        self.agency_color = agency_color  # Default: Elegant Dark Blue/Grey

    def generate_property_pdf(self, property_data: dict[str, Any], output_path: str) -> str:
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
            pdf.cell(0, 20, self.agency_name, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            pdf.set_font("Helvetica", "", 12)
            pdf.set_xy(10, 25)
            pdf.cell(0, 10, "Scheda Immobiliare Professionale", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

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
            pdf.cell(0, 10, f"Prezzo: {formatted_price}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(10)

            # --- Features Table ---
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, "Dettagli Proprietà:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Helvetica", "", 12)

            # Helper to handle None or missing values
            def format_val(val: Any, suffix: str = "") -> str:
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
                pdf.cell(0, 8, str(value), border="B", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            pdf.ln(10)

            # --- Description ---
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, "Descrizione:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(
                0, 7, property_data.get("description", "Nessuna descrizione disponibile.")
            )

            # --- Footer ---
            pdf.set_y(-30)
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(150, 150, 150)
            pdf.cell(
                0,
                10,
                f"Generato il {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                0,
                new_x=XPos.RIGHT,
                new_y=YPos.TOP,
                align="L",
            )
            pdf.cell(
                0,
                10,
                "Documento creato da Anzevino AI",
                0,
                new_x=XPos.RIGHT,
                new_y=YPos.TOP,
                align="R",
            )

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

    def generate_appraisal_report(self, appraisal_data: dict[str, Any], output_path: str) -> str:
        """
        Creates a professional PDF appraisal report with investment metrics.

        Args:
            appraisal_data: Dictionary containing property details, valuation, and metrics
            output_path: Where to save the generated PDF

        Returns:
            The path to the generated PDF
        """
        try:
            pdf = FPDF()
            pdf.add_page()

            # --- Header ---
            pdf.set_fill_color(*self.agency_color)
            pdf.rect(0, 0, 210, 35, "F")

            pdf.set_font("Helvetica", "B", 22)
            pdf.set_text_color(255, 255, 255)
            pdf.set_xy(10, 8)
            pdf.cell(
                0, 12, "Fifi AI - Valutazione Immobiliare", new_x=XPos.LMARGIN, new_y=YPos.NEXT
            )

            pdf.set_font("Helvetica", "", 10)
            pdf.set_xy(10, 22)
            pdf.cell(
                0,
                8,
                f"Generato il {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )

            pdf.set_text_color(0, 0, 0)
            pdf.set_y(45)

            # --- Property Address ---
            pdf.set_font("Helvetica", "B", 14)
            address = appraisal_data.get("address", "Indirizzo non specificato")
            pdf.cell(0, 10, f"Immobile: {address}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)

            # --- Executive Summary ---
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(0, 10, "Riepilogo Valutazione", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
            pdf.ln(2)

            predicted_value = appraisal_data.get("predicted_value", 0)
            confidence_range = appraisal_data.get("confidence_range", "N/A")
            confidence_level = appraisal_data.get("confidence_level", 0)

            pdf.set_font("Helvetica", "", 11)
            pdf.cell(
                0,
                8,
                f"Valore Stimato: EUR {predicted_value:,}".replace(",", "."),
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )
            pdf.cell(
                0,
                8,
                f"Range di Confidenza: {confidence_range}".replace("€", "EUR "),
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )
            pdf.cell(
                0,
                8,
                f"Livello di Confidenza: {confidence_level}%",
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )
            pdf.ln(5)

            # --- Property Details ---
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(0, 10, "Dettagli Proprietà", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
            pdf.ln(2)

            features = appraisal_data.get("features", {})
            pdf.set_font("Helvetica", "", 11)

            details = [
                ("Superficie", f"{features.get('sqm', 'N/A')} mq"),
                ("Camere", str(features.get("bedrooms", "N/A"))),
                ("Bagni", str(features.get("bathrooms", "N/A"))),
                ("Piano", str(features.get("floor", "N/A"))),
                ("Condizione", features.get("condition", "N/A")),
                ("Ascensore", "Sì" if features.get("has_elevator") else "No"),
                ("Balcone", "Sì" if features.get("has_balcony") else "No"),
            ]

            for label, value in details:
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(50, 7, f"{label}:", border="B")
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(0, 7, str(value), border="B", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            pdf.ln(5)

            # --- Investment Metrics ---
            metrics = appraisal_data.get("investment_metrics", {})
            if metrics:
                pdf.set_font("Helvetica", "B", 12)
                pdf.set_fill_color(240, 240, 240)
                pdf.cell(
                    0, 10, "Analisi Investimento", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True
                )
                pdf.ln(2)

                pdf.set_font("Helvetica", "", 11)
                monthly_rent = metrics.get("monthly_rent", 0)
                annual_rent = metrics.get("annual_rent", 0)
                cap_rate = metrics.get("cap_rate", 0)
                roi_5_year = metrics.get("roi_5_year", 0)
                cash_on_cash = metrics.get("cash_on_cash_return", 0)
                down_payment = metrics.get("down_payment_20pct", 0)

                investment_data = [
                    ("Affitto Mensile Stimato", f"EUR {monthly_rent:,}".replace(",", ".")),
                    ("Affitto Annuale", f"EUR {annual_rent:,}".replace(",", ".")),
                    ("Cap Rate (Rendimento Lordo)", f"{cap_rate}%"),
                    ("ROI (5 anni)", f"{roi_5_year}%"),
                    ("Cash-on-Cash Return", f"{cash_on_cash}%"),
                    ("Acconto Richiesto (20%)", f"EUR {down_payment:,}".replace(",", ".")),
                ]

                for label, value in investment_data:
                    pdf.set_font("Helvetica", "B", 10)
                    pdf.cell(70, 7, f"{label}:", border="B")
                    pdf.set_font("Helvetica", "", 10)
                    pdf.cell(0, 7, str(value), border="B", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

                pdf.ln(5)

            # --- Market Comparables ---
            comparables = appraisal_data.get("comparables", [])
            if comparables:
                pdf.set_font("Helvetica", "B", 12)
                pdf.set_fill_color(240, 240, 240)
                pdf.cell(
                    0, 10, "Immobili Comparabili", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True
                )
                pdf.ln(2)

                pdf.set_font("Helvetica", "", 9)
                for i, comp in enumerate(comparables[:3], 1):
                    title = comp.get("title", "N/A")
                    price = comp.get("sale_price_eur", 0)
                    sqm = comp.get("sqm", 0)
                    price_sqm = price / sqm if sqm > 0 else 0

                    pdf.set_font("Helvetica", "B", 10)
                    pdf.cell(0, 6, f"{i}. {title[:60]}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.set_font("Helvetica", "", 9)
                    pdf.cell(
                        0,
                        5,
                        f"   Prezzo: EUR {price:,} | {sqm} mq | EUR {price_sqm:,.0f}/mq".replace(
                            ",", "."
                        ),
                        new_x=XPos.LMARGIN,
                        new_y=YPos.NEXT,
                    )
                    pdf.ln(2)

                pdf.ln(3)

            # --- Disclaimer ---
            pdf.set_y(-50)
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(100, 100, 100)
            pdf.multi_cell(
                0,
                5,
                "DISCLAIMER: Questa valutazione è fornita solo a scopo informativo e non costituisce "
                "una perizia ufficiale. I valori stimati sono basati su algoritmi di machine learning "
                "e dati di mercato disponibili. Per decisioni di acquisto/vendita, si consiglia di "
                "consultare un perito certificato.",
            )

            pdf.set_y(-20)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(150, 150, 150)
            pdf.cell(
                0,
                5,
                "Powered by Fifi AI - Anzevino Real Estate Intelligence",
                0,
                new_x=XPos.RIGHT,
                new_y=YPos.TOP,
                align="C",
            )

            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            pdf.output(output_path)
            logger.info("APPRAISAL_PDF_GENERATED", context={"path": output_path})
            return output_path

        except Exception as e:
            logger.error("APPRAISAL_PDF_GENERATION_FAILED", context={"error": str(e)})
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
