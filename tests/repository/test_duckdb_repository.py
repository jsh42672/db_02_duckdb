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
            card_sets=[CardSetSeedDTO("Set A", 2020, "A-001", "Common", "(C)", 0.5)],
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

    def test_schema_splits_repeating_codes_for_bcnf(self) -> None:
        tables = {
            row[0]
            for row in self.connection.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'main'
                """
            ).fetchall()
        }
        self.assertTrue(
            {
                "price_source",
                "rarity",
                "ban_format",
                "ban_status_type",
                "deck_section",
                "role_tag",
                "deck_card_role",
            }.issubset(tables)
        )

        card_price_columns = {
            row[0]
            for row in self.connection.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'card_price'
                """
            ).fetchall()
        }
        self.assertEqual({"card_id", "source_name", "price"}, card_price_columns)

        set_entry_columns = {
            row[0]
            for row in self.connection.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'card_set_entry'
                """
            ).fetchall()
        }
        self.assertIn("rarity", set_entry_columns)
        self.assertNotIn("rarity_code", set_entry_columns)
        set_columns = {
            row[0]
            for row in self.connection.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'card_set'
                """
            ).fetchall()
        }
        self.assertIn("release_year", set_columns)

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

    def test_schema_repository_migrates_legacy_bcnf_tables(self) -> None:
        legacy_dir = tempfile.TemporaryDirectory()
        try:
            config = load_config(Path(legacy_dir.name))
            connection = create_connection(config.db_path)
            try:
                connection.execute(
                    """
                    CREATE TABLE card_type (name VARCHAR PRIMARY KEY);
                    CREATE TABLE attribute (name VARCHAR PRIMARY KEY);
                    CREATE TABLE race (name VARCHAR PRIMARY KEY);
                    CREATE TABLE archetype (name VARCHAR PRIMARY KEY);
                    CREATE TABLE card_set (name VARCHAR PRIMARY KEY);
                    CREATE TABLE card (
                        id BIGINT PRIMARY KEY,
                        name VARCHAR NOT NULL UNIQUE,
                        card_type VARCHAR NOT NULL,
                        frame_type VARCHAR,
                        attribute VARCHAR,
                        race VARCHAR,
                        level TINYINT,
                        atk SMALLINT,
                        def SMALLINT,
                        description TEXT,
                        is_extra_deck BOOLEAN NOT NULL DEFAULT FALSE
                    );
                    CREATE TABLE card_set_entry (
                        id BIGINT PRIMARY KEY,
                        card_id BIGINT NOT NULL,
                        set_name VARCHAR NOT NULL,
                        set_code VARCHAR,
                        rarity VARCHAR,
                        rarity_code VARCHAR,
                        set_price DECIMAL(10, 2)
                    );
                    CREATE TABLE ban_status (
                        card_id BIGINT NOT NULL,
                        format VARCHAR NOT NULL,
                        status VARCHAR NOT NULL,
                        PRIMARY KEY (card_id, format)
                    );
                    CREATE TABLE card_price (
                        card_id BIGINT PRIMARY KEY,
                        cardmarket DECIMAL(10, 2),
                        tcgplayer DECIMAL(10, 2),
                        ebay DECIMAL(10, 2),
                        amazon DECIMAL(10, 2),
                        coolstuffinc DECIMAL(10, 2)
                    );
                    CREATE TABLE deck (
                        id BIGINT PRIMARY KEY,
                        name VARCHAR NOT NULL,
                        memo TEXT,
                        ban_format VARCHAR NOT NULL DEFAULT 'TCG',
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE TABLE deck_card (
                        deck_id BIGINT NOT NULL,
                        card_id BIGINT NOT NULL,
                        section VARCHAR NOT NULL,
                        quantity TINYINT NOT NULL
                    );
                    CREATE TABLE card_archetype (card_id BIGINT, archetype_name VARCHAR);
                    CREATE TABLE card_image (image_id BIGINT PRIMARY KEY, card_id BIGINT, image_url TEXT, image_small TEXT, image_cropped TEXT);
                    CREATE TABLE seed_meta (key VARCHAR PRIMARY KEY, value VARCHAR NOT NULL);
                    INSERT INTO card_type VALUES ('Effect Monster');
                    INSERT INTO card_set VALUES ('Set A');
                    INSERT INTO card VALUES (100, 'Search Dragon', 'Effect Monster', 'effect', NULL, NULL, 4, 2000, 1500, 'Dragon', FALSE);
                    INSERT INTO card_set_entry VALUES (1, 100, 'Set A', 'A-001', 'Common', '(C)', 0.50);
                    INSERT INTO ban_status VALUES (100, 'TCG', 'Limited');
                    INSERT INTO card_price VALUES (100, 0.50, 0.60, NULL, NULL, NULL);
                    INSERT INTO deck VALUES (1, 'Legacy Deck', '', 'TCG', CURRENT_TIMESTAMP);
                    INSERT INTO deck_card VALUES (1, 100, 'MAIN', 2);
                    """
                )

                DuckDbSeedSchemaRepository(connection, config.schema_path).apply_schema()

                prices = connection.execute(
                    "SELECT source_name, price FROM card_price WHERE card_id = 100 ORDER BY source_name"
                ).fetchall()
                self.assertEqual(["cardmarket", "tcgplayer"], [row[0] for row in prices])
                self.assertEqual([0.50, 0.60], [float(row[1]) for row in prices])
                rarity_code = connection.execute("SELECT code FROM rarity WHERE name = 'Common'").fetchone()[0]
                self.assertEqual("(C)", rarity_code)
                set_columns = {
                    row[0]
                    for row in connection.execute(
                        """
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_name = 'card_set'
                        """
                    ).fetchall()
                }
                self.assertIn("release_year", set_columns)
                deck_total = connection.execute("SELECT SUM(quantity) FROM deck_card WHERE deck_id = 1").fetchone()[0]
                self.assertEqual(2, deck_total)
            finally:
                connection.close()
        finally:
            legacy_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
