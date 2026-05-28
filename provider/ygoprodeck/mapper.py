from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from domain.card.constants import EXTRA_DECK_MARKERS
from domain.seed.dto import CardImageSeedDTO, CardPriceSeedDTO, CardSetSeedDTO, SeedBanStatusDTO, SeedCardDTO


def to_int(value: Any) -> int | None:
    if value in (None, "", "?"):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def to_float(value: Any) -> float | None:
    if value in (None, "", "N/A"):
        return None
    try:
        return float(Decimal(str(value).replace(",", "")))
    except (InvalidOperation, ValueError):
        return None


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def is_extra_deck_card(card_type: str | None, frame_type: str | None) -> bool:
    text = f"{card_type or ''} {frame_type or ''}".lower()
    return any(marker in text for marker in EXTRA_DECK_MARKERS)


def map_api_cards(payload_cards: list[dict[str, Any]]) -> list[SeedCardDTO]:
    rows: list[SeedCardDTO] = []
    for raw in payload_cards:
        card_id = to_int(raw.get("id"))
        name = clean_text(raw.get("name"))
        card_type = clean_text(raw.get("type"))
        if card_id is None or not name or not card_type:
            continue

        frame_type = clean_text(raw.get("frameType"))
        ban_statuses: list[SeedBanStatusDTO] = []
        for api_key, ban_format in (("ban_tcg", "TCG"), ("ban_ocg", "OCG"), ("ban_goat", "GOAT")):
            status = (raw.get("banlist_info") or {}).get(api_key)
            if status:
                ban_statuses.append(SeedBanStatusDTO(format=ban_format, status=str(status)))

        rows.append(
            SeedCardDTO(
                id=card_id,
                name=name,
                card_type=card_type,
                frame_type=frame_type,
                description=clean_text(raw.get("desc")),
                atk=to_int(raw.get("atk")),
                def_=to_int(raw.get("def")),
                level=to_int(raw.get("level")),
                race=clean_text(raw.get("race")),
                attribute=clean_text(raw.get("attribute")),
                archetype=clean_text(raw.get("archetype")),
                is_extra_deck=is_extra_deck_card(card_type, frame_type),
                card_sets=[
                    CardSetSeedDTO(
                        set_name=clean_text(set_info.get("set_name")) or "",
                        set_code=clean_text(set_info.get("set_code")),
                        set_rarity=clean_text(set_info.get("set_rarity")),
                        set_rarity_code=clean_text(set_info.get("set_rarity_code")),
                        set_price=to_float(set_info.get("set_price")),
                    )
                    for set_info in (raw.get("card_sets") or [])
                    if clean_text(set_info.get("set_name"))
                ],
                card_prices=[
                    CardPriceSeedDTO(
                        cardmarket_price=to_float(price.get("cardmarket_price")),
                        tcgplayer_price=to_float(price.get("tcgplayer_price")),
                        ebay_price=to_float(price.get("ebay_price")),
                        amazon_price=to_float(price.get("amazon_price")),
                        coolstuffinc_price=to_float(price.get("coolstuffinc_price")),
                    )
                    for price in (raw.get("card_prices") or [])[:1]
                ],
                card_images=[
                    CardImageSeedDTO(
                        id=to_int(image.get("id")) or card_id,
                        image_url=clean_text(image.get("image_url")),
                        image_url_small=clean_text(image.get("image_url_small")),
                        image_url_cropped=clean_text(image.get("image_url_cropped")),
                    )
                    for image in (raw.get("card_images") or [])
                ],
                ban_statuses=ban_statuses,
            )
        )
    return rows
