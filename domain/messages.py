from typing import Literal, Optional

from pydantic import BaseModel


class Button(BaseModel):
    id: str
    title: str


class Row(BaseModel):
    id: str
    title: str
    description: Optional[str] = None


class Section(BaseModel):
    title: Optional[str] = None
    rows: list[Row]


class InteractiveMessage(BaseModel):
    type: Literal["button", "list", "cta_url"]
    body_text: str
    header_text: Optional[str] = None
    footer_text: Optional[str] = None

    # For Lists
    button_text: Optional[str] = None  # The text on the button that opens the list
    sections: Optional[list[Section]] = None

    # For Reply Buttons
    buttons: Optional[list[Button]] = None

    # For CTA URL
    url: Optional[str] = None
