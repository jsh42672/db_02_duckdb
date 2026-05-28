from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class CardSearchFilterDTO:
    keyword: str = ""
    card_type: str = ""
    attribute: str = ""
    race: str = ""
    archetype: str = ""
    level: str = ""
    atk_min: str = ""
    atk_max: str = ""
    def_min: str = ""
    def_max: str = ""
    limit: int = 100


@dataclass(slots=True)
class CardSummaryDTO:
    id: int
    name: str
    card_type: str
    attribute: str | None
    race: str | None
    level: int | None
    atk: int | None
    def_: int | None
    is_extra_deck: bool
    image_small: str | None
    archetypes: str | None


@dataclass(slots=True)
class CardPriceDTO:
    cardmarket: float | None = None
    tcgplayer: float | None = None
    ebay: float | None = None
    amazon: float | None = None
    coolstuffinc: float | None = None


@dataclass(slots=True)
class CardSetEntryDTO:
    set_name: str
    set_code: str | None
    rarity: str | None
    rarity_code: str | None
    set_price: float | None


@dataclass(slots=True)
class CardDetailDTO:
    id: int
    name: str
    card_type: str
    frame_type: str | None
    attribute: str | None
    race: str | None
    level: int | None
    atk: int | None
    def_: int | None
    description: str | None
    is_extra_deck: bool
    prices: CardPriceDTO
    image_url: str | None
    image_small: str | None
    image_cropped: str | None
    archetypes: str | None
    sets: list[CardSetEntryDTO] = field(default_factory=list)
    bans: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class LookupOptionsDTO:
    card_type: list[str]
    attribute: list[str]
    race: list[str]
    archetype: list[str]


@dataclass(slots=True)
class AppSummaryDTO:
    cards: int
    archetypes: int
    sets: int
    decks: int
    source: str
