import argparse

from mistralai import Mistral

from config import settings


class PitchGeneratorService:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.MISTRAL_API_KEY
        self.client = Mistral(api_key=self.api_key)

    def generate_pitch(self, property_details: str, style: str = "WhatsApp") -> str:
        prompt = f"""
        Sei un esperto di Social Media Marketing Immobiliare.
        Trasforma questi dettagli dell'immobile in un pitch `{style}` irresistibile
        per un potenziale acquirente. Usa emoji, sii persuasivo e professionale. Lingua: Italiano.

        DETTAGLI IMMOBILE:
        {property_details}
        """

        try:
            chat_response = self.client.chat.complete(
                model="mistral-tiny",
                messages=[{"role": "user", "content": prompt}],
            )
            if chat_response and chat_response.choices:
                content = chat_response.choices[0].message.content
                return str(content) if content else ""
            return ""
        except Exception as e:
            return f"Error: {e}"


# Backward compatibility
def generate_pitch(property_details: str, style: str = "WhatsApp") -> str:
    service = PitchGeneratorService()
    return service.generate_pitch(property_details, style)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Property Pitch Generator")
    parser.add_argument("--details", type=str, required=True, help="Property details")
    parser.add_argument(
        "--style",
        type=str,
        default="WhatsApp",
        choices=["WhatsApp", "Email", "Instagram"],
        help="Style",
    )

    args = parser.parse_args()

    print("\n" + "=" * 50)
    print(f"🪄  GENERA PITCH {args.style.upper()}")
    print("=" * 50 + "\n")

    pitch = generate_pitch(args.details, args.style)
    print(pitch)
    print("\n" + "=" * 50 + "\n")
