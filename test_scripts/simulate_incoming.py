from config.container import container
from domain.enums import LeadStatus


def simulate(phone: str, text: str):
    print(f"Simulating incoming message from {phone}: {text}")

    # 1. Ensure lead is active and AI mode is ON
    lead = container.db.get_lead(phone)
    if not lead:
        print(f"Creating lead for {phone}")
        container.db.save_lead(
            {
                "customer_phone": phone,
                "customer_name": "Test Lead Verification",
                "status": LeadStatus.ACTIVE,
                "is_ai_active": True,
            }
        )
    else:
        print(f"Lead exists. is_ai_active={lead.get('is_ai_active')}")
        container.db.update_lead(phone, {"is_ai_active": True})

    # 2. Process incoming message
    response = container.lead_processor.process_incoming_message(phone=phone, text=text)

    print(f"AI Response: {response}")


if __name__ == "__main__":
    # Use a fresh test number
    simulate("+393999888777", "Ciao, cerco una casa a Firenze con budget 300k")
