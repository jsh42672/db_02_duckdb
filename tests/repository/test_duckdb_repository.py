from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.config import load_config
from domain.card.dto import CardSearchFilterDTO
from domain.deck.dto import DeckItemDTO
from domain.seed.dto import CardImageSeedDTO, CardPriceSeedDTO, CardSetSeedDTO, SeedBanStatusDTO, SeedCardDTO
from repository.duckdb.card.detail_repository import DuckDbCardDetailRepository
from repository.duckdb.card.lookup_repository import DuckDbLookupRepository
from repository.duckdb.card.query_repository import DuckDbCardQueryRepository
from repository.duckdb.connection import create_connection
from repository.duckdb.deck.command_repository import DuckDbDeckCommandRepository
from repository.duckdb.deck.query_repository import DuckDbDeckQueryRepository
from repository.duckdb.seed.bulk_insert_repository import DuckDbSeedBulkInsertRepository
from repository.duckdb.seed.meta_repository import DuckDbSeedMetaRepository
from repository.duckdb.seed.schema_repository import DuckDbSeedSchemaRepository


def build_seed_cards() -> list[SeedCardDTO]:
    return [
        SeedCardDTO(
            id=100,
            name="Search Dragon",
            card_type="Effect Monster",
            frame_type="effect",
            description="Dragon test card",
            atk=2000,
            def_=1500,
            level=4,
            race="Dragon",
            attribute="LIGHT",
            archetype="Test",
            is_extra_deck=False,
            card_sets=[CardSetSeedDTO("Set A", "A-001", "Common", "(C)", 0.5)],
            card_prices=[CardPriceSeedDTO(0.5, 0.6, 0.7, 0.8, 0.9)],
            card_images=[CardImageSeedDTO(100, "image-100", "image-100-small", "image-100-cropped")],
            ban_statuses=[SeedBanStatusDTO("TCG", "Limited")],
        ),
        SeedCardDTO(
            id=101,
            name="Plain Spell",
            card_type="Spell Card",
            frame_type="spell",
            description="No price or image",
            atk=None,
            def_=None,
            level=None,
            race="Normal",
            attribute=None,
            archetype=None,
            is_extra_deck=False,
        ),
        SeedCardDTO(
            id=102,
            name="Extra Dragon",
            card_type="Fusion Monster",
            frame_type="fusion",
            description="Extra deck card",
            atk=2500,
            def_=2000,
            level=8,
            race="Dragon",
            attribute="DARK",
            archetype="Test",
            is_extra_deck=True,
        ),
    ]


class TestDuckDbRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        config = load_config(Path(self.temp_dir.name))
        self.connection = create_connection(config.db_path)
        self.meta_repository = DuckDbSeedMetaRepository(self.connection)
        self.schema_repository = DuckDbSeedSchemaRepository(self.connection, config.schema_path)
        self.bulk_insert_repository = DuckDbSeedBulkInsertRepository(self.connection, self.meta_repository)
        self.schema_repository.apply_schema()
        self.bulk_insert_repository.seed_cards(build_seed_cards(), "test")

    def tearDown(self) -> None:
        self.connection.close()
        self.temp_dir.cleanup()

    def test_card_search_supports_keyword_and_filter(self) -> None:
        repository = DuckDbCardQueryRepository(self.connection)
        cards = repository.search_cards(
            CardSearchFilterDTO(keyword="Dragon", race="Dragon", attribute="LIGHT")
        )
        self.assertEqual(1, len(cards))
        self.assertEqual("Search Dragon", cards[0].name)

    def test_card_detail_returns_card_without_optional_related_rows(self) -> None:
        repository = DuckDbCardDetailRepository(self.connection)
        detail = repository.get_card_detail(101)
        self.assertIsNotNone(detail)
        assert detail is not None
        self.assertEqual("Plain Spell", detail.name)
        self.assertIsNone(detail.prices.tcgplayer)
        self.assertEqual([], detail.sets)
        self.assertEqual({}, detail.bans)

    def test_deck_roundtrip_save_list_detail_delete(self) -> None:
        command_repository = DuckDbDeckCommandRepository(self.connection)
        query_repository = DuckDbDeckQueryRepository(self.connection)

        deck_id = command_repository.save_deck(
            "Repo Deck",
            "repository test",
            "TCG",
            [
                DeckItemDTO(card_id=100, section="MAIN", quantity=3),
                DeckItemDTO(card_id=101, section="MAIN", quantity=2),
                DeckItemDTO(card_id=102, section="EXTRA", quantity=1),
            ],
        )
        summaries = query_repository.list_decks()
        self.assertEqual(1, len(summaries))
        self.assertEqual(deck_id, summaries[0].id)

        detail = query_repository.get_deck_detail(deck_id)
        self.assertIsNotNone(detail)
        assert detail is not None
        self.assertEqual(3, len(detail.cards))

        command_repository.delete_deck(deck_id)
        self.assertEqual([], query_repository.list_decks())


if __name__ == "__main__":
    unittest.main()
