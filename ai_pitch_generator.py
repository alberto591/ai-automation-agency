import os
import argparse
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)

def generate_pitch(property_details, style="WhatsApp"):
    """Generates a high-converting sales pitch using Mistral."""
    
    prompt = f"""
    Sei un esperto di Social Media Marketing Immobiliare.
    Trasforma questi dettagli dell'immobile in un pitch `{style}` irresistibile per un potenziale acquirente.
    Usa emoji, sii persuasivo e professionale. Lingua: Italiano.

    DETTAGLI IMMOBILE:
    {property_details}
    """
    
    try:
        chat_response = client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}],
        )
        return chat_response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Property Pitch Generator")
    parser.add_argument("--details", type=str, required=True, help="Property details (e.g., 'Attico 150mq Milano vista Duomo')")
    parser.add_argument("--style", type=str, default="WhatsApp", choices=["WhatsApp", "Email", "Instagram"], help="Style of the pitch")
    
    args = parser.parse_args()
    
    print("\n" + "="*50)
    print(f"🪄  GENERA PITCH {args.style.upper()}")
    print("="*50 + "\n")
    
    pitch = generate_pitch(args.details, args.style)
    print(pitch)
    print("\n" + "="*50 + "\n")
