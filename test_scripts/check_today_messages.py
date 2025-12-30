import json

from config.container import container


def check_today_messages():
    try:
        res = (
            container.db.client.table("messages")
            .select("*, leads(customer_phone)")
            .gte("created_at", "2025-12-30T00:00:00Z")
            .execute()
        )
        print(f"Messages from today: {len(res.data)}")
        if res.data:
            print(json.dumps(res.data, indent=2))
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    check_today_messages()
