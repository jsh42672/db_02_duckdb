from __future__ import annotations

from domain.card.constants import EXTRA_DECK_MARKERS
from domain.seed.dto import CardImageSeedDTO, CardPriceSeedDTO, CardSetSeedDTO, SeedBanStatusDTO, SeedCardDTO


FALLBACK_CARDS: list[dict[str, object]] = [
    {
        "id": 89631139,
        "name": "Blue-Eyes White Dragon",
        "type": "Normal Monster",
        "frameType": "normal",
        "desc": "This legendary dragon is a powerful engine of destruction.",
        "atk": 3000,
        "def": 2500,
        "level": 8,
        "race": "Dragon",
        "attribute": "LIGHT",
        "archetype": "Blue-Eyes",
    },
    {
        "id": 38517737,
        "name": "Blue-Eyes Alternative White Dragon",
        "type": "Effect Monster",
        "frameType": "effect",
        "desc": "Cannot be Normal Summoned/Set. Must first be Special Summoned.",
        "atk": 3000,
        "def": 2500,
        "level": 8,
        "race": "Dragon",
        "attribute": "LIGHT",
        "archetype": "Blue-Eyes",
    },
    {
        "id": 46986414,
        "name": "Dark Magician",
        "type": "Normal Monster",
        "frameType": "normal",
        "desc": "The ultimate wizard in terms of attack and defense.",
        "atk": 2500,
        "def": 2100,
        "level": 7,
        "race": "Spellcaster",
        "attribute": "DARK",
        "archetype": "Dark Magician",
    },
    {
        "id": 38033121,
        "name": "Dark Magician Girl",
        "type": "Effect Monster",
        "frameType": "effect",
        "desc": "Gains 300 ATK for every Dark Magician in the GYs.",
        "atk": 2000,
        "def": 1700,
        "level": 6,
        "race": "Spellcaster",
        "attribute": "DARK",
        "archetype": "Dark Magician",
    },
    {
        "id": 14558127,
        "name": "Ash Blossom & Joyous Spring",
        "type": "Tuner Monster",
        "frameType": "effect",
        "desc": "When a card or effect is activated that adds from Deck, Special Summons from Deck, or sends from Deck to GY: discard this card; negate that effect.",
        "atk": 0,
        "def": 1800,
        "level": 3,
        "race": "Zombie",
        "attribute": "FIRE",
    },
    {
        "id": 23434538,
        "name": 'Maxx "C"',
        "type": "Effect Monster",
        "frameType": "effect",
        "desc": "During either player's turn: send this card from your hand to the GY; this turn, each time your opponent Special Summons, draw 1 card.",
        "atk": 500,
        "def": 200,
        "level": 2,
        "race": "Insect",
        "attribute": "EARTH",
        "banlist_info": {"ban_tcg": "Forbidden", "ban_ocg": "Semi-Limited"},
    },
    {
        "id": 24224830,
        "name": "Called by the Grave",
        "type": "Spell Card",
        "frameType": "spell",
        "desc": "Target 1 monster in your opponent's GY; banish it, and if you do, negate its effects.",
        "race": "Quick-Play",
        "banlist_info": {"ban_tcg": "Limited", "ban_ocg": "Limited"},
    },
    {
        "id": 10045474,
        "name": "Infinite Impermanence",
        "type": "Trap Card",
        "frameType": "trap",
        "desc": "Target 1 face-up monster your opponent controls; negate its effects until the end of this turn.",
        "race": "Normal",
    },
    {
        "id": 12580477,
        "name": "Raigeki",
        "type": "Spell Card",
        "frameType": "spell",
        "desc": "Destroy all monsters your opponent controls.",
        "race": "Normal",
        "banlist_info": {"ban_ocg": "Limited"},
    },
    {
        "id": 83764718,
        "name": "Monster Reborn",
        "type": "Spell Card",
        "frameType": "spell",
        "desc": "Target 1 monster in either GY; Special Summon it.",
        "race": "Normal",
        "banlist_info": {"ban_tcg": "Limited", "ban_ocg": "Limited"},
    },
    {
        "id": 5318639,
        "name": "Mystical Space Typhoon",
        "type": "Spell Card",
        "frameType": "spell",
        "desc": "Target 1 Spell/Trap on the field; destroy that target.",
        "race": "Quick-Play",
    },
    {
        "id": 24094653,
        "name": "Polymerization",
        "type": "Spell Card",
        "frameType": "spell",
        "desc": "Fusion Summon 1 Fusion Monster from your Extra Deck.",
        "race": "Normal",
    },
    {
        "id": 44095762,
        "name": "Mirror Force",
        "type": "Trap Card",
        "frameType": "trap",
        "desc": "When an opponent's monster declares an attack: destroy all your opponent's Attack Position monsters.",
        "race": "Normal",
    },
    {
        "id": 97268402,
        "name": "Effect Veiler",
        "type": "Tuner Monster",
        "frameType": "effect",
        "desc": "During your opponent's Main Phase: send this card from your hand to the GY, then target 1 Effect Monster your opponent controls; negate its effects until the end of this turn.",
        "atk": 0,
        "def": 0,
        "level": 1,
        "race": "Spellcaster",
        "attribute": "LIGHT",
    },
    {
        "id": 27204311,
        "name": "Nibiru, the Primal Being",
        "type": "Effect Monster",
        "frameType": "effect",
        "desc": "During the Main Phase, if your opponent Normal or Special Summoned 5 or more monsters this turn: Tribute as many face-up monsters on the field as possible.",
        "atk": 3000,
        "def": 600,
        "level": 11,
        "race": "Rock",
        "attribute": "LIGHT",
    },
    {
        "id": 14087893,
        "name": "Book of Moon",
        "type": "Spell Card",
        "frameType": "spell",
        "desc": "Target 1 face-up monster on the field; change that target to face-down Defense Position.",
        "race": "Quick-Play",
    },
    {
        "id": 41420027,
        "name": "Solemn Judgment",
        "type": "Trap Card",
        "frameType": "trap",
        "desc": "When a monster would be Summoned, or a Spell/Trap Card is activated: pay half your LP; negate the Summon or activation, and if you do, destroy that card.",
        "race": "Counter",
    },
    {
        "id": 44508094,
        "name": "Stardust Dragon",
        "type": "Synchro Monster",
        "frameType": "synchro",
        "desc": "1 Tuner + 1+ non-Tuner monsters.",
        "atk": 2500,
        "def": 2000,
        "level": 8,
        "race": "Dragon",
        "attribute": "WIND",
    },
    {
        "id": 84013237,
        "name": "Number 39: Utopia",
        "type": "XYZ Monster",
        "frameType": "xyz",
        "desc": "2 Level 4 monsters.",
        "atk": 2500,
        "def": 2000,
        "level": 4,
        "race": "Warrior",
        "attribute": "LIGHT",
    },
    {
        "id": 1861629,
        "name": "Decode Talker",
        "type": "Link Monster",
        "frameType": "link",
        "desc": "2+ Effect Monsters.",
        "atk": 2300,
        "race": "Cyberse",
        "attribute": "DARK",
    },
]


def _is_extra_deck(card_type: str | None, frame_type: str | None) -> bool:
    text = f"{card_type or ''} {frame_type or ''}".lower()
    return any(marker in text for marker in EXTRA_DECK_MARKERS)


def _image_payload(card_id: int) -> list[CardImageSeedDTO]:
    return [
        CardImageSeedDTO(
            id=card_id,
            image_url=f"https://images.ygoprodeck.com/images/cards/{card_id}.jpg",
            image_url_small=f"https://images.ygoprodeck.com/images/cards_small/{card_id}.jpg",
            image_url_cropped=f"https://images.ygoprodeck.com/images/cards_cropped/{card_id}.jpg",
        )
    ]


def fallback_cards() -> list[SeedCardDTO]:
    rows: list[SeedCardDTO] = []
    for raw in FALLBACK_CARDS:
        ban_statuses: list[SeedBanStatusDTO] = []
        for api_key, ban_format in (("ban_tcg", "TCG"), ("ban_ocg", "OCG"), ("ban_goat", "GOAT")):
            status = (raw.get("banlist_info") or {}).get(api_key)  # type: ignore[union-attr]
            if status:
                ban_statuses.append(SeedBanStatusDTO(format=ban_format, status=str(status)))

        rows.append(
            SeedCardDTO(
                id=int(raw["id"]),
                name=str(raw["name"]),
                card_type=str(raw["type"]),
                frame_type=str(raw.get("frameType") or "") or None,
                description=str(raw.get("desc") or "") or None,
                atk=int(raw["atk"]) if raw.get("atk") is not None else None,
                def_=int(raw["def"]) if raw.get("def") is not None else None,
                level=int(raw["level"]) if raw.get("level") is not None else None,
                race=str(raw.get("race") or "") or None,
                attribute=str(raw.get("attribute") or "") or None,
                archetype=str(raw.get("archetype") or "") or None,
                is_extra_deck=_is_extra_deck(str(raw["type"]), str(raw.get("frameType") or "")),
                card_sets=[
                    CardSetSeedDTO(
                        set_name="Sample Classroom Pack",
                        release_year=2024,
                        set_code=f"SAMPLE-{int(raw['id']) % 1000:03d}",
                        set_rarity="Common",
                        set_rarity_code="(C)",
                        set_price=0.20,
                    )
                ],
                card_prices=[
                    CardPriceSeedDTO(
                        cardmarket_price=0.20,
                        tcgplayer_price=0.25,
                        ebay_price=0.99,
                        amazon_price=1.49,
                        coolstuffinc_price=0.35,
                    )
                ],
                card_images=_image_payload(int(raw["id"])),
                ban_statuses=ban_statuses,
            )
        )
    return rows
