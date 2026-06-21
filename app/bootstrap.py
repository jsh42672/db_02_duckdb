from __future__ import annotations

from dataclasses import dataclass

import duckdb

from app.config import AppConfig, load_config
from provider.ygoprodeck.provider import YgoProDeckProvider
from repository.duckdb.card.detail_repository import DuckDbCardDetailRepository
from repository.duckdb.card.lookup_repository import DuckDbLookupRepository
from repository.duckdb.card.query_repository import DuckDbCardQueryRepository
from repository.duckdb.connection import create_connection
from repository.duckdb.deck.command_repository import DuckDbDeckCommandRepository
from repository.duckdb.deck.query_repository import DuckDbDeckQueryRepository
from repository.duckdb.deck.validation_repository import DuckDbDeckValidationRepository
from repository.duckdb.seed.bulk_insert_repository import DuckDbSeedBulkInsertRepository
from repository.duckdb.seed.meta_repository import DuckDbSeedMetaRepository
from repository.duckdb.seed.schema_repository import DuckDbSeedSchemaRepository
from service.card.detail_service import DefaultCardDetailService
from service.card.lookup_service import DefaultLookupService
from service.card.search_service import DefaultCardSearchService
from service.deck.builder_service import DefaultDeckBuilderService
from service.deck.saved_deck_service import DefaultSavedDeckService
from service.deck.validation_service import DefaultDeckValidationService
from service.seed.initialize_service import DefaultInitializeService


@dataclass(slots=True)
class AppContainer:
    config: AppConfig
    connection: duckdb.DuckDBPyConnection
    initialize_service: DefaultInitializeService
    search_service: DefaultCardSearchService
    detail_service: DefaultCardDetailService
    lookup_service: DefaultLookupService
    deck_builder_service: DefaultDeckBuilderService
    deck_validation_service: DefaultDeckValidationService
    saved_deck_service: DefaultSavedDeckService

    def close(self) -> None:
        self.connection.close()


def build_app_container() -> AppContainer:
    config = load_config()
    connection = create_connection(config.db_path)

    # 외부 데이터 공급자와 DuckDB 구현체는 이 조립 지점에서만 직접 생성한다.
    provider = YgoProDeckProvider(config)

    card_query_repository = DuckDbCardQueryRepository(connection)
    card_detail_repository = DuckDbCardDetailRepository(connection)
    lookup_repository = DuckDbLookupRepository(connection)
    deck_query_repository = DuckDbDeckQueryRepository(connection)
    deck_command_repository = DuckDbDeckCommandRepository(connection)
    deck_validation_repository = DuckDbDeckValidationRepository(connection)
    meta_repository = DuckDbSeedMetaRepository(connection)
    schema_repository = DuckDbSeedSchemaRepository(connection, config.schema_path)
    bulk_insert_repository = DuckDbSeedBulkInsertRepository(connection, meta_repository)

    # Service에는 구체적인 DB 연결 대신 Repository Interface 역할의 객체를 주입한다.
    detail_service = DefaultCardDetailService(card_detail_repository)
    validation_service = DefaultDeckValidationService(deck_validation_repository)
    saved_deck_service = DefaultSavedDeckService(
        deck_command_repository,
        deck_query_repository,
        validation_service,
    )
    initialize_service = DefaultInitializeService(
        provider,
        card_query_repository,
        deck_query_repository,
        lookup_repository,
        schema_repository,
        meta_repository,
        bulk_insert_repository,
    )

    # View가 필요한 기능만 꺼내 쓸 수 있도록 조립된 객체를 하나의 Container로 반환한다.
    return AppContainer(
        config=config,
        connection=connection,
        initialize_service=initialize_service,
        search_service=DefaultCardSearchService(card_query_repository),
        detail_service=detail_service,
        lookup_service=DefaultLookupService(lookup_repository),
        deck_builder_service=DefaultDeckBuilderService(deck_validation_repository, detail_service),
        deck_validation_service=validation_service,
        saved_deck_service=saved_deck_service,
    )
