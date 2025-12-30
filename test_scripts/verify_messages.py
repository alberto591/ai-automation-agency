from config.container import container


def verify_messages():
    phone = "+393999888777"

    # Get messages for this specific lead
    try:
        lead = container.db.get_lead(phone)
        if not lead:
            print(f"Lead {phone} not found.")
            return

        lead_id = lead["id"]

        # Fetch messages for this lead
        res = (
            container.db.client.table("messages")
            .select("*")
            .eq("lead_id", lead_id)
            .order("created_at")
            .execute()
        )

        messages = res.data
        print(f"Total messages for {phone}: {len(messages)}")
        print("\nMessages:")
        for msg in messages:
            print(f"  - [{msg['role']}] {msg['content'][:50]}... (created: {msg['created_at']})")

        # Check for duplicates
        contents = [m["content"] for m in messages]
        duplicates = len(contents) - len(set(contents))
        print(f"\nDuplicate messages: {duplicates}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    verify_messages()
