from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class CardSetSeedDTO:
    set_name: str
    set_code: str | None
    set_rarity: str | None
    set_rarity_code: str | None
    set_price: float | None


@dataclass(slots=True)
class CardPriceSeedDTO:
    cardmarket_price: float | None
    tcgplayer_price: float | None
    ebay_price: float | None
    amazon_price: float | None
    coolstuffinc_price: float | None


@dataclass(slots=True)
class CardImageSeedDTO:
    id: int
    image_url: str | None
    image_url_small: str | None
    image_url_cropped: str | None


@dataclass(slots=True)
class SeedBanStatusDTO:
    format: str
    status: str


@dataclass(slots=True)
class SeedCardDTO:
    id: int
    name: str
    card_type: str
    frame_type: str | None
    description: str | None
    atk: int | None
    def_: int | None
    level: int | None
    race: str | None
    attribute: str | None
    archetype: str | None
    is_extra_deck: bool
    card_sets: list[CardSetSeedDTO] = field(default_factory=list)
    card_prices: list[CardPriceSeedDTO] = field(default_factory=list)
    card_images: list[CardImageSeedDTO] = field(default_factory=list)
    ban_statuses: list[SeedBanStatusDTO] = field(default_factory=list)
