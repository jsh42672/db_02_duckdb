from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.config import load_config
from domain.seed.dto import SeedCardDTO
from provider.ygoprodeck.fallback import fallback_cards
from repository.duckdb.card.lookup_repository import DuckDbLookupRepository
from repository.duckdb.card.query_repository import DuckDbCardQueryRepository
from repository.duckdb.connection import create_connection
from repository.duckdb.deck.query_repository import DuckDbDeckQueryRepository
from repository.duckdb.seed.bulk_insert_repository import DuckDbSeedBulkInsertRepository
from repository.duckdb.seed.meta_repository import DuckDbSeedMetaRepository
from repository.duckdb.seed.schema_repository import DuckDbSeedSchemaRepository
from service.seed.initialize_service import DefaultInitializeService


class StubProvider:
    def __init__(self, cards: list[SeedCardDTO], source: str):
        self.cards = cards
        self.source = source
        self.calls = 0

    def fetch_cards(self) -> tuple[list[SeedCardDTO], str]:
        self.calls += 1
        return self.cards, self.source


class TestInitializeService(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config = load_config(Path(self.temp_dir.name))
        self.connection = create_connection(self.config.db_path)
        self.card_query_repository = DuckDbCardQueryRepository(self.connection)
        self.deck_query_repository = DuckDbDeckQueryRepository(self.connection)
        self.lookup_repository = DuckDbLookupRepository(self.connection)
        self.meta_repository = DuckDbSeedMetaRepository(self.connection)
        self.schema_repository = DuckDbSeedSchemaRepository(self.connection, self.config.schema_path)
        self.bulk_insert_repository = DuckDbSeedBulkInsertRepository(self.connection, self.meta_repository)

    def tearDown(self) -> None:
        self.connection.close()
        self.temp_dir.cleanup()

    def build_service(self, provider: StubProvider) -> DefaultInitializeService:
        return DefaultInitializeService(
            provider,
            self.card_query_repository,
            self.deck_query_repository,
            self.lookup_repository,
            self.schema_repository,
            self.meta_repository,
            self.bulk_insert_repository,
        )

    def test_initializes_empty_database(self) -> None:
        provider = StubProvider(fallback_cards()[:2], "fallback")
        summary = self.build_service(provider).initialize()
        self.assertEqual(1, provider.calls)
        self.assertEqual("fallback", summary.source)
        self.assertEqual(2, summary.cards)

    def test_replaces_fallback_catalog_when_provider_has_more_cards(self) -> None:
        self.schema_repository.apply_schema()
        self.bulk_insert_repository.seed_cards(fallback_cards()[:1], "fallback")
        provider = StubProvider(fallback_cards()[:3], "cache")
        summary = self.build_service(provider).initialize()
        self.assertEqual(1, provider.calls)
        self.assertEqual("cache", summary.source)
        self.assertEqual(3, summary.cards)

    def test_keeps_cache_seed_without_reloading(self) -> None:
        self.schema_repository.apply_schema()
        self.bulk_insert_repository.seed_cards(fallback_cards()[:2], "cache")
        provider = StubProvider(fallback_cards()[:4], "api")
        summary = self.build_service(provider).initialize()
        self.assertEqual(0, provider.calls)
        self.assertEqual("cache", summary.source)
        self.assertEqual(2, summary.cards)


if __name__ == "__main__":
    unittest.main()
