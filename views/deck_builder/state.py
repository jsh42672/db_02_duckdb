from __future__ import annotations

from dataclasses import dataclass, field

from domain.deck.constants import SECTIONS
from domain.deck.dto import DeckItemDTO


@dataclass(slots=True)
class DeckBuilderState:
    deck_items: dict[str, dict[int, DeckItemDTO]] = field(
        default_factory=lambda: {section: {} for section in SECTIONS}
    )
