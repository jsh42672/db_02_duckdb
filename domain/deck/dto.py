from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class DeckItemDTO:
    card_id: int
    section: str
    quantity: int
    name: str = ""
    card_type: str = ""
    is_extra_deck: bool = False
    ban_status: str | None = None


@dataclass(slots=True)
class SaveDeckRequestDTO:
    name: str
    memo: str
    ban_format: str
    items: list[DeckItemDTO]


@dataclass(slots=True)
class DeckValidationResultDTO:
    ok: bool
    messages: list[str]


@dataclass(slots=True)
class SavedDeckSummaryDTO:
    id: int
    name: str
    ban_format: str
    created_at: object
    total_cards: int


@dataclass(slots=True)
class SavedDeckCardDTO:
    section: str
    quantity: int
    card_id: int
    name: str
    card_type: str
    is_extra_deck: bool
    ban_status: str | None = None


@dataclass(slots=True)
class SavedDeckDetailDTO:
    id: int
    name: str
    memo: str | None
    ban_format: str
    created_at: object
    cards: list[SavedDeckCardDTO] = field(default_factory=list)
