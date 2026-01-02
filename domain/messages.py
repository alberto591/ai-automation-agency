from typing import Literal

from pydantic import BaseModel


class Button(BaseModel):
    id: str
    title: str


class Row(BaseModel):
    id: str
    title: str
    description: str | None = None


class Section(BaseModel):
    title: str | None = None
    rows: list[Row]


class InteractiveMessage(BaseModel):
    type: Literal["button", "list", "cta_url"]
    body_text: str
    header_text: str | None = None
    footer_text: str | None = None

    # For Lists
    button_text: str | None = None  # The text on the button that opens the list
    sections: list[Section] | None = None

    # For Reply Buttons
    buttons: list[Button] | None = None

    # For CTA URL
    url: str | None = None
