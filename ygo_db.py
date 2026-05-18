from __future__ import annotations

import json
import urllib.error
import urllib.request
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "ygo_cards.duckdb"
CACHE_PATH = DATA_DIR / "ygo_cards_cache.json"
SCHEMA_PATH = ROOT_DIR / "sql" / "schema.sql"
API_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php"

EXTRA_DECK_MARKERS = ("fusion", "synchro", "xyz", "link")
BAN_FORMATS = ("TCG", "OCG", "GOAT")
SECTIONS = ("MAIN", "EXTRA", "SIDE")


FALLBACK_CARDS: list[dict[str, Any]] = [
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


def is_extra_deck_card(card_type: str | None, frame_type: str | None = None) -> bool:
    text = f"{card_type or ''} {frame_type or ''}".lower()
    return any(marker in text for marker in EXTRA_DECK_MARKERS)


def to_int(value: Any) -> int | None:
    if value in (None, "", "?"):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def to_decimal(value: Any) -> float | None:
    if value in (None, "", "N/A"):
        return None
    try:
        return float(Decimal(str(value).replace(",", "")))
    except (InvalidOperation, ValueError):
        return None


def status_to_limit(status: str | None) -> int:
    if not status:
        return 3
    normalized = status.lower()
    if "forbidden" in normalized or "banned" in normalized:
        return 0
    if "semi" in normalized:
        return 2
    if "limited" in normalized:
        return 1
    return 3


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def image_payload(card_id: int) -> list[dict[str, Any]]:
    return [
        {
            "id": card_id,
            "image_url": f"https://images.ygoprodeck.com/images/cards/{card_id}.jpg",
            "image_url_small": f"https://images.ygoprodeck.com/images/cards_small/{card_id}.jpg",
            "image_url_cropped": f"https://images.ygoprodeck.com/images/cards_cropped/{card_id}.jpg",
        }
    ]


def fallback_cards() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in FALLBACK_CARDS:
        card = dict(raw)
        card["card_images"] = image_payload(card["id"])
        card["card_prices"] = [
            {
                "cardmarket_price": "0.20",
                "tcgplayer_price": "0.25",
                "ebay_price": "0.99",
                "amazon_price": "1.49",
                "coolstuffinc_price": "0.35",
            }
        ]
        card["card_sets"] = [
            {
                "set_name": "Sample Classroom Pack",
                "set_code": f"SAMPLE-{card['id'] % 1000:03d}",
                "set_rarity": "Common",
                "set_rarity_code": "(C)",
                "set_price": "0.20",
            }
        ]
        rows.append(card)
    return rows


def fetch_api_cards() -> tuple[list[dict[str, Any]], str]:
    if CACHE_PATH.exists():
        payload = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        return payload.get("data", payload), "cache"

    request = urllib.request.Request(
        API_URL,
        headers={"User-Agent": "db-term-project-ygo/1.0"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        payload = json.loads(response.read().decode("utf-8"))

    CACHE_PATH.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return payload.get("data", payload), "api"


class YgoRepository:
    def __init__(self, db_path: Path = DB_PATH):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self.con = duckdb.connect(str(db_path))

    def close(self) -> None:
        self.con.close()

    def initialize(self) -> dict[str, Any]:
        self.apply_schema()
        card_count = self.card_count()
        seed_source = self.meta_value("seed_source")
        if card_count == 0:
            try:
                cards, source = fetch_api_cards()
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
                cards, source = fallback_cards(), "fallback"
            self.seed_cards(cards, source)
        elif seed_source == "fallback" and self.deck_count() == 0 and CACHE_PATH.exists():
            cards, source = fetch_api_cards()
            if len(cards) > card_count:
                self.replace_catalog(cards, source)
        return self.summary()

    def apply_schema(self) -> None:
        self.con.execute(SCHEMA_PATH.read_text(encoding="utf-8"))

    def card_count(self) -> int:
        return self.con.execute("SELECT COUNT(*) FROM card").fetchone()[0]

    def deck_count(self) -> int:
        return self.con.execute("SELECT COUNT(*) FROM deck").fetchone()[0]

    def meta_value(self, key: str) -> str | None:
        row = self.con.execute("SELECT value FROM seed_meta WHERE key = ?", [key]).fetchone()
        return row[0] if row else None

    def summary(self) -> dict[str, Any]:
        row = self.con.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM card) AS cards,
                (SELECT COUNT(*) FROM archetype) AS archetypes,
                (SELECT COUNT(*) FROM card_set) AS sets,
                (SELECT COUNT(*) FROM deck) AS decks
            """
        ).fetchone()
        meta = {
            key: value
            for key, value in self.con.execute("SELECT key, value FROM seed_meta").fetchall()
        }
        return {
            "cards": row[0],
            "archetypes": row[1],
            "sets": row[2],
            "decks": row[3],
            "source": meta.get("seed_source", "unknown"),
        }

    def replace_catalog(self, api_cards: list[dict[str, Any]], source: str) -> None:
        for table in (
            "deck_card",
            "deck",
            "card_image",
            "card_price",
            "ban_status",
            "card_set_entry",
            "card_archetype",
            "card",
            "card_set",
            "archetype",
            "race",
            "attribute",
            "card_type",
            "seed_meta",
        ):
            self.con.execute(f"DROP TABLE IF EXISTS {table}")
        self.apply_schema()
        self.seed_cards(api_cards, source)

    def seed_cards(self, api_cards: list[dict[str, Any]], source: str) -> None:
        card_types: set[str] = set()
        attributes: set[str] = set()
        races: set[str] = set()
        archetypes: set[str] = set()
        set_names: set[str] = set()

        cards: list[tuple[Any, ...]] = []
        card_archetypes: set[tuple[int, str]] = set()
        set_entries: list[tuple[Any, ...]] = []
        set_entry_keys: set[tuple[Any, ...]] = set()
        ban_rows: set[tuple[int, str, str]] = set()
        price_rows: dict[int, tuple[Any, ...]] = {}
        image_rows: dict[int, tuple[Any, ...]] = {}

        set_entry_id = 1

        for raw in api_cards:
            card_id = to_int(raw.get("id"))
            name = clean_text(raw.get("name"))
            card_type = clean_text(raw.get("type"))
            if card_id is None or not name or not card_type:
                continue

            frame_type = clean_text(raw.get("frameType"))
            attribute = clean_text(raw.get("attribute"))
            race = clean_text(raw.get("race"))
            archetype_name = clean_text(raw.get("archetype"))

            card_types.add(card_type)
            if attribute:
                attributes.add(attribute)
            if race:
                races.add(race)
            if archetype_name:
                archetypes.add(archetype_name)
                card_archetypes.add((card_id, archetype_name))

            cards.append(
                (
                    card_id,
                    name,
                    card_type,
                    frame_type,
                    attribute,
                    race,
                    to_int(raw.get("level")),
                    to_int(raw.get("atk")),
                    to_int(raw.get("def")),
                    raw.get("desc"),
                    is_extra_deck_card(card_type, frame_type),
                )
            )

            for set_info in raw.get("card_sets") or []:
                set_name = clean_text(set_info.get("set_name"))
                if not set_name:
                    continue
                set_names.add(set_name)
                key = (
                    card_id,
                    set_info.get("set_code"),
                    set_info.get("set_rarity"),
                )
                if key in set_entry_keys:
                    continue
                set_entry_keys.add(key)
                set_entries.append(
                    (
                        set_entry_id,
                        card_id,
                        set_name,
                        set_info.get("set_code"),
                        set_info.get("set_rarity"),
                        set_info.get("set_rarity_code"),
                        to_decimal(set_info.get("set_price")),
                    )
                )
                set_entry_id += 1

            ban_info = raw.get("banlist_info") or {}
            for api_key, ban_format in (
                ("ban_tcg", "TCG"),
                ("ban_ocg", "OCG"),
                ("ban_goat", "GOAT"),
            ):
                status = ban_info.get(api_key)
                if status:
                    ban_rows.add((card_id, ban_format, status))

            prices = raw.get("card_prices") or []
            if prices:
                price = prices[0]
                price_rows[card_id] = (
                    card_id,
                    to_decimal(price.get("cardmarket_price")),
                    to_decimal(price.get("tcgplayer_price")),
                    to_decimal(price.get("ebay_price")),
                    to_decimal(price.get("amazon_price")),
                    to_decimal(price.get("coolstuffinc_price")),
                )

            for image in raw.get("card_images") or []:
                image_id = to_int(image.get("id"))
                if image_id is None:
                    continue
                image_rows[image_id] = (
                    image_id,
                    card_id,
                    image.get("image_url"),
                    image.get("image_url_small"),
                    image.get("image_url_cropped"),
                )

        self.con.execute("BEGIN TRANSACTION")
        try:
            self.bulk_insert("card_type", ["name"], [(name,) for name in sorted(card_types)])
            self.bulk_insert("attribute", ["name"], [(name,) for name in sorted(attributes)])
            self.bulk_insert("race", ["name"], [(name,) for name in sorted(races)])
            self.bulk_insert("archetype", ["name"], [(name,) for name in sorted(archetypes)])
            self.bulk_insert("card_set", ["name"], [(name,) for name in sorted(set_names)])
            self.bulk_insert(
                "card",
                [
                    "id",
                    "name",
                    "card_type",
                    "frame_type",
                    "attribute",
                    "race",
                    "level",
                    "atk",
                    "def",
                    "description",
                    "is_extra_deck",
                ],
                cards,
            )
            self.bulk_insert(
                "card_archetype",
                ["card_id", "archetype_name"],
                sorted(card_archetypes),
            )
            self.bulk_insert(
                "card_set_entry",
                ["id", "card_id", "set_name", "set_code", "rarity", "rarity_code", "set_price"],
                set_entries,
            )
            self.bulk_insert(
                "ban_status",
                ["card_id", "format", "status"],
                sorted(ban_rows),
            )
            self.bulk_insert(
                "card_price",
                ["card_id", "cardmarket", "tcgplayer", "ebay", "amazon", "coolstuffinc"],
                list(price_rows.values()),
            )
            self.bulk_insert(
                "card_image",
                ["image_id", "card_id", "image_url", "image_small", "image_cropped"],
                list(image_rows.values()),
            )
            self.set_meta("seed_source", source)
            self.set_meta("seed_card_count", str(len(cards)))
            self.con.execute("COMMIT")
        except Exception:
            self.con.execute("ROLLBACK")
            raise

    def set_meta(self, key: str, value: str) -> None:
        self.con.execute("DELETE FROM seed_meta WHERE key = ?", [key])
        self.con.execute("INSERT INTO seed_meta VALUES (?, ?)", [key, value])

    def bulk_insert(self, table: str, columns: list[str], rows: list[tuple[Any, ...]]) -> None:
        if not rows:
            return
        frame = pd.DataFrame(rows, columns=columns)
        view_name = "_bulk_rows"
        quoted_columns = ", ".join(f'"{column}"' for column in columns)
        self.con.register(view_name, frame)
        try:
            self.con.execute(
                f'INSERT INTO "{table}" ({quoted_columns}) SELECT {quoted_columns} FROM {view_name}'
            )
        finally:
            self.con.unregister(view_name)

    def options(self) -> dict[str, list[str]]:
        def names(table: str) -> list[str]:
            rows = self.con.execute(f"SELECT name FROM {table} ORDER BY name").fetchall()
            return [row[0] for row in rows]

        return {
            "card_type": names("card_type"),
            "attribute": names("attribute"),
            "race": names("race"),
            "archetype": names("archetype"),
        }

    def search_cards(
        self,
        keyword: str = "",
        card_type: str = "",
        attribute: str = "",
        race: str = "",
        archetype: str = "",
        level: str = "",
        atk_min: str = "",
        atk_max: str = "",
        def_min: str = "",
        def_max: str = "",
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: list[Any] = []

        if keyword.strip():
            term = f"%{keyword.strip()}%"
            conditions.append("(c.name ILIKE ? OR c.description ILIKE ?)")
            params.extend([term, term])
        if card_type:
            conditions.append("c.card_type = ?")
            params.append(card_type)
        if attribute:
            conditions.append("c.attribute = ?")
            params.append(attribute)
        if race:
            conditions.append("c.race = ?")
            params.append(race)
        if archetype:
            conditions.append(
                """
                EXISTS (
                    SELECT 1
                    FROM card_archetype ca2
                    WHERE ca2.card_id = c.id
                      AND ca2.archetype_name = ?
                )
                """
            )
            params.append(archetype)

        numeric_filters = (
            ("c.level = ?", level),
            ("c.atk >= ?", atk_min),
            ("c.atk <= ?", atk_max),
            ("c.def >= ?", def_min),
            ("c.def <= ?", def_max),
        )
        for expression, raw_value in numeric_filters:
            value = to_int(raw_value)
            if value is not None:
                conditions.append(expression)
                params.append(value)

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        params.append(limit)
        rows = self.con.execute(
            f"""
            SELECT
                c.id,
                c.name,
                c.card_type,
                c.attribute,
                c.race,
                c.level,
                c.atk,
                c.def,
                c.is_extra_deck,
                img.image_small,
                string_agg(DISTINCT ca.archetype_name, ', ') AS archetypes
            FROM card c
            LEFT JOIN card_archetype ca ON ca.card_id = c.id
            LEFT JOIN (
                SELECT card_id, MIN(image_small) AS image_small
                FROM card_image
                GROUP BY card_id
            ) img ON img.card_id = c.id
            {where_clause}
            GROUP BY
                c.id, c.name, c.card_type, c.attribute, c.race, c.level,
                c.atk, c.def, c.is_extra_deck, img.image_small
            ORDER BY c.name
            LIMIT ?
            """,
            params,
        ).fetchall()

        return [
            {
                "id": row[0],
                "name": row[1],
                "card_type": row[2],
                "attribute": row[3],
                "race": row[4],
                "level": row[5],
                "atk": row[6],
                "def": row[7],
                "is_extra_deck": row[8],
                "image_small": row[9],
                "archetypes": row[10],
            }
            for row in rows
        ]

    def card_detail(self, card_id: int) -> dict[str, Any] | None:
        row = self.con.execute(
            """
            SELECT
                c.id,
                c.name,
                c.card_type,
                c.frame_type,
                c.attribute,
                c.race,
                c.level,
                c.atk,
                c.def,
                c.description,
                c.is_extra_deck,
                p.cardmarket,
                p.tcgplayer,
                p.ebay,
                p.amazon,
                p.coolstuffinc,
                img.image_url,
                img.image_small,
                img.image_cropped,
                string_agg(DISTINCT ca.archetype_name, ', ') AS archetypes
            FROM card c
            LEFT JOIN card_price p ON p.card_id = c.id
            LEFT JOIN (
                SELECT
                    card_id,
                    MIN(image_url) AS image_url,
                    MIN(image_small) AS image_small,
                    MIN(image_cropped) AS image_cropped
                FROM card_image
                GROUP BY card_id
            ) img ON img.card_id = c.id
            LEFT JOIN card_archetype ca ON ca.card_id = c.id
            WHERE c.id = ?
            GROUP BY
                c.id, c.name, c.card_type, c.frame_type, c.attribute, c.race,
                c.level, c.atk, c.def, c.description, c.is_extra_deck,
                p.cardmarket, p.tcgplayer, p.ebay, p.amazon, p.coolstuffinc,
                img.image_url, img.image_small, img.image_cropped
            """,
            [card_id],
        ).fetchone()
        if row is None:
            return None

        sets = self.con.execute(
            """
            SELECT set_name, set_code, rarity, rarity_code, set_price
            FROM card_set_entry
            WHERE card_id = ?
            ORDER BY set_name, set_code
            LIMIT 20
            """,
            [card_id],
        ).fetchall()
        bans = self.con.execute(
            """
            SELECT format, status
            FROM ban_status
            WHERE card_id = ?
            ORDER BY format
            """,
            [card_id],
        ).fetchall()

        return {
            "id": row[0],
            "name": row[1],
            "card_type": row[2],
            "frame_type": row[3],
            "attribute": row[4],
            "race": row[5],
            "level": row[6],
            "atk": row[7],
            "def": row[8],
            "description": row[9],
            "is_extra_deck": row[10],
            "prices": {
                "cardmarket": row[11],
                "tcgplayer": row[12],
                "ebay": row[13],
                "amazon": row[14],
                "coolstuffinc": row[15],
            },
            "image_url": row[16],
            "image_small": row[17],
            "image_cropped": row[18],
            "archetypes": row[19],
            "sets": [
                {
                    "set_name": item[0],
                    "set_code": item[1],
                    "rarity": item[2],
                    "rarity_code": item[3],
                    "set_price": item[4],
                }
                for item in sets
            ],
            "bans": {item[0]: item[1] for item in bans},
        }

    def validate_deck(
        self,
        items: list[dict[str, Any]],
        ban_format: str = "TCG",
    ) -> tuple[bool, list[str]]:
        messages: list[str] = []
        totals = {section: 0 for section in SECTIONS}
        by_card: dict[int, int] = {}

        if not items:
            return False, ["Deck is empty."]

        card_ids = sorted({int(item["card_id"]) for item in items})
        placeholders = ", ".join("?" for _ in card_ids)
        card_rows = self.con.execute(
            f"""
            SELECT id, name, is_extra_deck
            FROM card
            WHERE id IN ({placeholders})
            """,
            card_ids,
        ).fetchall()
        cards = {
            row[0]: {"name": row[1], "is_extra_deck": row[2]}
            for row in card_rows
        }
        ban_rows = self.con.execute(
            f"""
            SELECT card_id, status
            FROM ban_status
            WHERE format = ?
              AND card_id IN ({placeholders})
            """,
            [ban_format, *card_ids],
        ).fetchall()
        bans = {row[0]: row[1] for row in ban_rows}

        for item in items:
            card_id = int(item["card_id"])
            section = item["section"]
            quantity = int(item["quantity"])
            totals[section] += quantity
            by_card[card_id] = by_card.get(card_id, 0) + quantity

            card = cards.get(card_id)
            if not card:
                messages.append(f"Unknown card id: {card_id}")
                continue
            if card["is_extra_deck"] and section == "MAIN":
                messages.append(f"{card['name']} must be placed in the Extra Deck.")
            if not card["is_extra_deck"] and section == "EXTRA":
                messages.append(f"{card['name']} cannot be placed in the Extra Deck.")

        if not 40 <= totals["MAIN"] <= 60:
            messages.append("Main Deck must contain 40 to 60 cards.")
        if not 0 <= totals["EXTRA"] <= 15:
            messages.append("Extra Deck must contain 0 to 15 cards.")
        if not 0 <= totals["SIDE"] <= 15:
            messages.append("Side Deck must contain 0 to 15 cards.")

        for card_id, quantity in by_card.items():
            status = bans.get(card_id)
            limit = status_to_limit(status)
            if quantity > limit:
                name = cards.get(card_id, {}).get("name", str(card_id))
                status_text = status or "Unlimited"
                messages.append(f"{name}: {quantity} copies exceeds {ban_format} {status_text} limit.")

        return not messages, messages or ["Deck is legal."]

    def save_deck(
        self,
        name: str,
        memo: str,
        ban_format: str,
        items: list[dict[str, Any]],
    ) -> int:
        ok, messages = self.validate_deck(items, ban_format)
        if not ok:
            raise ValueError("\n".join(messages))

        deck_id = self.con.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM deck").fetchone()[0]
        self.con.execute("BEGIN TRANSACTION")
        try:
            self.con.execute(
                "INSERT INTO deck (id, name, memo, ban_format) VALUES (?, ?, ?, ?)",
                [deck_id, name, memo, ban_format],
            )
            rows = [
                (deck_id, int(item["card_id"]), item["section"], int(item["quantity"]))
                for item in items
            ]
            self.con.executemany(
                "INSERT INTO deck_card VALUES (?, ?, ?, ?)",
                rows,
            )
            self.con.execute("COMMIT")
        except Exception:
            self.con.execute("ROLLBACK")
            raise
        return int(deck_id)

    def list_decks(self) -> list[dict[str, Any]]:
        rows = self.con.execute(
            """
            SELECT
                d.id,
                d.name,
                d.ban_format,
                d.created_at,
                COALESCE(SUM(dc.quantity), 0) AS total_cards
            FROM deck d
            LEFT JOIN deck_card dc ON dc.deck_id = d.id
            GROUP BY d.id, d.name, d.ban_format, d.created_at
            ORDER BY d.created_at DESC
            """
        ).fetchall()
        return [
            {
                "id": row[0],
                "name": row[1],
                "ban_format": row[2],
                "created_at": row[3],
                "total_cards": row[4],
            }
            for row in rows
        ]

    def deck_detail(self, deck_id: int) -> dict[str, Any] | None:
        deck = self.con.execute(
            "SELECT id, name, memo, ban_format, created_at FROM deck WHERE id = ?",
            [deck_id],
        ).fetchone()
        if deck is None:
            return None

        rows = self.con.execute(
            """
            SELECT
                dc.section,
                dc.quantity,
                c.id,
                c.name,
                c.card_type,
                c.is_extra_deck,
                b.status
            FROM deck_card dc
            JOIN card c ON c.id = dc.card_id
            JOIN deck d ON d.id = dc.deck_id
            LEFT JOIN ban_status b ON b.card_id = c.id AND b.format = d.ban_format
            WHERE dc.deck_id = ?
            ORDER BY dc.section, c.name
            """,
            [deck_id],
        ).fetchall()
        return {
            "id": deck[0],
            "name": deck[1],
            "memo": deck[2],
            "ban_format": deck[3],
            "created_at": deck[4],
            "cards": [
                {
                    "section": row[0],
                    "quantity": row[1],
                    "card_id": row[2],
                    "name": row[3],
                    "card_type": row[4],
                    "is_extra_deck": row[5],
                    "ban_status": row[6],
                }
                for row in rows
            ],
        }

    def delete_deck(self, deck_id: int) -> None:
        self.con.execute("DELETE FROM deck_card WHERE deck_id = ?", [deck_id])
        self.con.execute("DELETE FROM deck WHERE id = ?", [deck_id])

    def sample_deck_items(self, ban_format: str = "TCG") -> list[dict[str, Any]]:
        main_candidates = self._legal_candidates(False, ban_format)
        extra_candidates = self._legal_candidates(True, ban_format)
        items: list[dict[str, Any]] = []

        main_count = 0
        for card in main_candidates:
            if main_count >= 40:
                break
            quantity = min(card["limit"], 3, 40 - main_count)
            if quantity <= 0:
                continue
            items.append({"card_id": card["id"], "section": "MAIN", "quantity": quantity})
            main_count += quantity

        for card in extra_candidates[:5]:
            items.append({"card_id": card["id"], "section": "EXTRA", "quantity": 1})

        return items

    def _legal_candidates(self, extra_deck: bool, ban_format: str) -> list[dict[str, Any]]:
        rows = self.con.execute(
            """
            SELECT
                c.id,
                c.name,
                COALESCE(b.status, '') AS status
            FROM card c
            LEFT JOIN ban_status b ON b.card_id = c.id AND b.format = ?
            WHERE c.is_extra_deck = ?
            ORDER BY c.name
            LIMIT 200
            """,
            [ban_format, extra_deck],
        ).fetchall()
        return [
            {"id": row[0], "name": row[1], "limit": status_to_limit(row[2])}
            for row in rows
            if status_to_limit(row[2]) > 0
        ]
