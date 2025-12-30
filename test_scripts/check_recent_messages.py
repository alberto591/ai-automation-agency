import json

from config.container import container


def check_recent_messages():
    try:
        res = (
            container.db.client.table("messages")
            .select("*, leads(customer_phone)")
            .order("created_at")
            .execute()
        )
        print("Most Recent Messages across all leads:")
        # Reverse and take 10
        data = res.data[::-1][:10]
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    check_recent_messages()
