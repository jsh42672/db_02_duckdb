from __future__ import annotations

from typing import Any

from domain.seed.dto import SeedCardDTO
from repository.duckdb.base import BaseDuckDbRepository


class DuckDbSeedBulkInsertRepository(BaseDuckDbRepository):
    def __init__(self, connection, meta_repository):
        super().__init__(connection)
        self.meta_repository = meta_repository

    def seed_cards(self, cards: list[SeedCardDTO], source: str) -> None:
        # API의 중첩 배열을 정규화된 테이블별 행 집합으로 먼저 분리한다.
        card_types: set[str] = set()
        attributes: set[str] = set()
        races: set[str] = set()
        archetypes: set[str] = set()
        card_sets: set[str] = set()
        rarities: dict[str, str | None] = {}
        ban_formats: set[str] = set()
        ban_status_types: set[str] = set()

        card_rows: list[tuple[Any, ...]] = []
        card_archetypes: set[tuple[int, str]] = set()
        set_entries: list[tuple[Any, ...]] = []
        set_entry_keys: set[tuple[Any, ...]] = set()
        ban_rows: set[tuple[int, str, str]] = set()
        price_rows: set[tuple[int, str, float]] = set()
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

            # 수록 세트는 API 중복을 제거한 뒤 관계 테이블의 대체키를 부여한다.
            for set_info in card.card_sets:
                if not set_info.set_name:
                    continue
                card_sets.add(set_info.set_name)
                key = (card.id, set_info.set_code, set_info.set_rarity)
                if key in set_entry_keys:
                    continue
                set_entry_keys.add(key)
                if set_info.set_rarity:
                    if set_info.set_rarity not in rarities or rarities[set_info.set_rarity] is None:
                        rarities[set_info.set_rarity] = set_info.set_rarity_code
                set_entries.append(
                    (
                        set_entry_id,
                        card.id,
                        set_info.set_name,
                        set_info.set_code,
                        set_info.set_rarity,
                        set_info.set_price,
                    )
                )
                set_entry_id += 1

            for ban_status in card.ban_statuses:
                ban_formats.add(ban_status.format)
                ban_status_types.add(ban_status.status)
                ban_rows.add((card.id, ban_status.format, ban_status.status))

            # 판매처별 가격을 반복 컬럼이 아닌 source_name별 행으로 변환한다.
            if card.card_prices:
                price = card.card_prices[0]
                source_values = (
                    ("cardmarket", price.cardmarket_price),
                    ("tcgplayer", price.tcgplayer_price),
                    ("ebay", price.ebay_price),
                    ("amazon", price.amazon_price),
                    ("coolstuffinc", price.coolstuffinc_price),
                )
                for source_name, source_price in source_values:
                    if source_price is not None:
                        price_rows.add((card.id, source_name, source_price))

            for image in card.card_images:
                image_rows[image.id] = (
                    image.id,
                    card.id,
                    image.image_url,
                    image.image_url_small,
                    image.image_url_cropped,
                )

        # 코드 테이블과 관계 테이블 전체가 함께 저장되도록 하나의 트랜잭션으로 처리한다.
        self.con.execute("BEGIN TRANSACTION")
        try:
            self.bulk_insert("card_type", ["name"], [(name,) for name in sorted(card_types)])
            self.bulk_insert("attribute", ["name"], [(name,) for name in sorted(attributes)])
            self.bulk_insert("race", ["name"], [(name,) for name in sorted(races)])
            self.bulk_insert("archetype", ["name"], [(name,) for name in sorted(archetypes)])
            self.bulk_insert("card_set", ["name"], [(name,) for name in sorted(card_sets)])
            self.bulk_insert("rarity", ["name", "code"], sorted(rarities.items()))
            self.bulk_insert("ban_format", ["name"], [(name,) for name in sorted(ban_formats)])
            self.bulk_insert("ban_status_type", ["name"], [(name,) for name in sorted(ban_status_types)])
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
                ["id", "card_id", "set_name", "set_code", "rarity", "set_price"],
                set_entries,
            )
            self.bulk_insert("ban_status", ["card_id", "format", "status"], sorted(ban_rows))
            self.bulk_insert(
                "card_price",
                ["card_id", "source_name", "price"],
                sorted(price_rows),
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
