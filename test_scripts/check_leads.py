import json

from config.container import container


def check_leads():
    phone = "+393331234567"
    lead = container.db.get_lead(phone)
    if lead:
        print(f"Lead Found: {lead.get('customer_name')} ({phone})")
        print(f"Status: {lead.get('status')}")
        print(f"AI Active: {lead.get('is_ai_active')}")
        print("Messages count:", len(lead.get("messages", [])))
        print("Last 2 Messages:")
        print(json.dumps(lead.get("messages", [])[-2:], indent=2))
    else:
        print(f"Lead {phone} not found.")


if __name__ == "__main__":
    check_leads()
