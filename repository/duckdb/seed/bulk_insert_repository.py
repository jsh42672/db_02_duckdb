from __future__ import annotations

from typing import Any

from domain.seed.dto import SeedCardDTO
from repository.duckdb.base import BaseDuckDbRepository


class DuckDbSeedBulkInsertRepository(BaseDuckDbRepository):
    def __init__(self, connection, meta_repository):
        super().__init__(connection)
        self.meta_repository = meta_repository

    def seed_cards(self, cards: list[SeedCardDTO], source: str) -> None:
        card_types: set[str] = set()
        attributes: set[str] = set()
        races: set[str] = set()
        archetypes: set[str] = set()
        set_names: set[str] = set()

        card_rows: list[tuple[Any, ...]] = []
        card_archetypes: set[tuple[int, str]] = set()
        set_entries: list[tuple[Any, ...]] = []
        set_entry_keys: set[tuple[Any, ...]] = set()
        ban_rows: set[tuple[int, str, str]] = set()
        price_rows: dict[int, tuple[Any, ...]] = {}
        image_rows: dict[int, tuple[Any, ...]] = {}
        set_entry_id = 1

        for card in cards:
            card_types.add(card.card_type)
            if card.attribute:
                attributes.add(card.attribute)
            if card.race:
                races.add(card.race)
            if card.archetype:
                archetypes.add(card.archetype)
                card_archetypes.add((card.id, card.archetype))

            card_rows.append(
                (
                    card.id,
                    card.name,
                    card.card_type,
                    card.frame_type,
                    card.attribute,
                    card.race,
                    card.level,
                    card.atk,
                    card.def_,
                    card.description,
                    card.is_extra_deck,
                )
            )

            for set_info in card.card_sets:
                if not set_info.set_name:
                    continue
                set_names.add(set_info.set_name)
                key = (card.id, set_info.set_code, set_info.set_rarity)
                if key in set_entry_keys:
                    continue
                set_entry_keys.add(key)
                set_entries.append(
                    (
                        set_entry_id,
                        card.id,
                        set_info.set_name,
                        set_info.set_code,
                        set_info.set_rarity,
                        set_info.set_rarity_code,
                        set_info.set_price,
                    )
                )
                set_entry_id += 1

            for ban_status in card.ban_statuses:
                ban_rows.add((card.id, ban_status.format, ban_status.status))

            if card.card_prices:
                price = card.card_prices[0]
                price_rows[card.id] = (
                    card.id,
                    price.cardmarket_price,
                    price.tcgplayer_price,
                    price.ebay_price,
                    price.amazon_price,
                    price.coolstuffinc_price,
                )

            for image in card.card_images:
                image_rows[image.id] = (
                    image.id,
                    card.id,
                    image.image_url,
                    image.image_url_small,
                    image.image_url_cropped,
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
                card_rows,
            )
            self.bulk_insert("card_archetype", ["card_id", "archetype_name"], sorted(card_archetypes))
            self.bulk_insert(
                "card_set_entry",
                ["id", "card_id", "set_name", "set_code", "rarity", "rarity_code", "set_price"],
                set_entries,
            )
            self.bulk_insert("ban_status", ["card_id", "format", "status"], sorted(ban_rows))
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
            self.meta_repository.set_meta_value("seed_source", source)
            self.meta_repository.set_meta_value("seed_card_count", str(len(card_rows)))
            self.con.execute("COMMIT")
        except Exception:
            self.con.execute("ROLLBACK")
            raise
