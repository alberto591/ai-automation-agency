import os
from datetime import datetime
from typing import Any

from fpdf import FPDF

from domain.ports import DocumentPort
from infrastructure.ai_pdf_generator import PropertyPDFGenerator
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class DocumentAdapter(DocumentPort):
    def __init__(self, output_dir: str = "temp/documents") -> None:
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_pdf(self, template_name: str, data: dict[str, Any]) -> str:
        """
        Generates a professional PDF brochure or document based on the template.
        """
        try:
            if template_name == "brochure":
                generator = PropertyPDFGenerator()
                filename = f"brochure_{data.get('id', 'unknown')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
                filepath = os.path.join(self.output_dir, filename)
                return generator.generate_property_pdf(data, filepath)

            if template_name == "sales_report":
                generator = PropertyPDFGenerator()
                filename = f"sales_report_{data.get('property_id', 'unknown')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
                filepath = os.path.join(self.output_dir, filename)
                return generator.generate_sales_report(data, filepath)

            # Fallback to simplistic PDF for other templates (like 'proposta')
            pdf = FPDF()
            pdf.add_page()

            # Header
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "PROPOSTA D'ACQUISTO IMMOBILIARE", ln=True, align="C")
            pdf.ln(10)

            # Body
            pdf.set_font("Helvetica", "", 12)
            pdf.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
            pdf.cell(0, 10, f"Promissario Acquirente: {data.get('customer_name', 'N/A')}", ln=True)
            pdf.cell(0, 10, f"Telefono: {data.get('customer_phone', 'N/A')}", ln=True)
            pdf.ln(5)

            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, "Dettagli Offerta:", ln=True)
            pdf.set_font("Helvetica", "", 12)
            pdf.cell(0, 10, f"Prezzo Offerto: {data.get('offered_price', 'N/A')} EUR", ln=True)
            pdf.ln(10)

            # Footer
            pdf.set_font("Helvetica", "I", 8)
            pdf.cell(
                0,
                10,
                "Generato da Anzevino AI - Agenzia Immobiliare Innovativa",
                ln=True,
                align="C",
            )

            filename = f"proposta_{data.get('customer_phone', 'unknown')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            pdf.output(filepath)

            logger.info("DOCUMENT_GENERATED", context={"path": filepath})
            return filepath  # In production, this would be a URL to Supabase Storage
        except Exception as e:
            logger.error("DOCUMENT_GENERATION_FAILED", context={"error": str(e)})
            return ""
