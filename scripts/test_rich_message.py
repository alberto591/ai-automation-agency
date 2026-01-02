import asyncio
import os
import sys
from typing import Any

# Ensure project root is in path
sys.path.append(os.getcwd())

from domain.ports import MessagingPort


# Mock Adapter for testing without real creds if needed, or use MetaAdapter if env vars set
class MockRichAdapter(MessagingPort):
    def send_message(self, to: str, body: str, media_url: str | None = None) -> str:
        print(f"Sending Text: {body}")
        return "msg_123"

    def send_interactive_message(self, to: str, message: Any) -> str:
        print(f"\n✅ SENDING RICH MESSAGE to {to}")
        print(f"Type: {message.type}")
        if message.type == "list":
            print(f"Button: {message.button_text}")
            for sec in message.sections:
                print(f"Section: {sec.title}")
                for row in sec.rows:
                    print(f" - {row.title}: {row.description}")
        return "msg_rich_123"


async def test_rich_message():
    print("--- Testing Rich Message Payload ---")

    # Switch to real adapter if you have credentials, otherwise Mock
    adapter = MockRichAdapter()

    from domain.messages import InteractiveMessage, Row, Section

    rows = [
        Row(id="p1", title="Villa Florence", description="€1,200,000"),
        Row(id="p2", title="Apartment Center", description="€450,000"),
    ]

    msg = InteractiveMessage(
        type="list",
        body_text="Here are the best properties found for you:",
        button_text="View Homes",
        sections=[Section(title="Results", rows=rows)],
    )

    adapter.send_interactive_message("+393331234567", msg)


if __name__ == "__main__":
    asyncio.run(test_rich_message())
