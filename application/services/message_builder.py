from typing import Any

from domain.messages import Button, InteractiveMessage, Row, Section


class MessageBuilder:
    """Helper service to construct Interactive Messages (Buttons, Lists) for WhatsApp."""

    @staticmethod
    def create_qualification_buttons(
        header: str = "Come possimo aiutarti?", body: str = "Seleziona un'opzione:"
    ) -> InteractiveMessage:
        return InteractiveMessage(
            type="button",
            header_text=header,
            body_text=body,
            buttons=[
                Button(id="intent_buy", title="🏠 Comprare"),
                Button(id="intent_rent", title="🔑 Affittare"),
                Button(id="intent_sell", title="💰 Vendere"),
            ],
        )

    @staticmethod
    def create_budget_buttons(
        header: str = "Qual è il tuo budget?", body: str = "Seleziona una fascia:"
    ) -> InteractiveMessage:
        return InteractiveMessage(
            type="list",
            header_text=header,
            body_text=body,
            button_text="Seleziona Budget",
            sections=[
                Section(
                    title="Budget",
                    rows=[
                        Row(id="budget_under_200k", title="< €200k"),
                        Row(id="budget_200k_400k", title="€200k - €400k"),
                        Row(id="budget_400k_600k", title="€400k - €600k"),
                        Row(id="budget_over_600k", title="> €600k"),
                    ],
                )
            ],
        )

    @staticmethod
    def create_confirmation_buttons(
        body: str = "Confermi?", yes_id: str = "yes", no_id: str = "no"
    ) -> InteractiveMessage:
        return InteractiveMessage(
            type="button",
            body_text=body,
            buttons=[
                Button(id=yes_id, title="✅ Sì"),
                Button(id=no_id, title="❌ No"),
            ],
        )

    @staticmethod
    def create_property_list(
        properties: list[dict[str, Any]], header: str = "Immobili trovati"
    ) -> InteractiveMessage:
        """Creates a list message from property data."""
        rows = []
        for p in properties[:10]:  # Meta limit is 10 rows
            rows.append(
                Row(
                    id=f"prop_{p.get('id', 'unknown')}",
                    title=p.get("title", "Immobile")[:24],
                    description=f"€{p.get('price', 0):,} - {p.get('zone', '')}"[:72],
                )
            )

        return InteractiveMessage(
            type="list",
            header_text=header,
            body_text=f"Abbiamo trovato {len(properties)} immobili per te:",
            button_text="Vedi Immobili",
            sections=[Section(title="Risultati", rows=rows)],
        )
