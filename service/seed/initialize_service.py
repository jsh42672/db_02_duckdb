from __future__ import annotations

from domain.card.dto import AppSummaryDTO
from provider.interfaces import ICardDataProvider
from repository.interfaces import (
    ICardQueryRepository,
    IDeckQueryRepository,
    ILookupRepository,
    ISeedBulkInsertRepository,
    ISeedMetaRepository,
    ISeedSchemaRepository,
)


class DefaultInitializeService:
    def __init__(
        self,
        provider: ICardDataProvider,
        card_query_repository: ICardQueryRepository,
        deck_query_repository: IDeckQueryRepository,
        lookup_repository: ILookupRepository,
        schema_repository: ISeedSchemaRepository,
        meta_repository: ISeedMetaRepository,
        bulk_insert_repository: ISeedBulkInsertRepository,
    ):
        self.provider = provider
        self.card_query_repository = card_query_repository
        self.deck_query_repository = deck_query_repository
        self.lookup_repository = lookup_repository
        self.schema_repository = schema_repository
        self.meta_repository = meta_repository
        self.bulk_insert_repository = bulk_insert_repository

    def initialize(self) -> AppSummaryDTO:
        # 어떤 데이터가 저장되어 있더라도 먼저 최신 DDL과 호환되도록 스키마를 맞춘다.
        self.schema_repository.apply_schema()
        card_count = self.card_query_repository.card_count()
        seed_source = self.meta_repository.get_meta_value("seed_source")
        if card_count == 0:
            # 최초 실행에서는 Provider가 선택한 API/cache/fallback 데이터를 그대로 시딩한다.
            cards, source = self.provider.fetch_cards()
            self.bulk_insert_repository.seed_cards(cards, source)
        elif seed_source == "fallback" and self.deck_query_repository.deck_count() == 0:
            # 임시 fallback만 있고 사용자 덱이 없을 때에만 더 큰 카드 카탈로그로 교체한다.
            cards, source = self.provider.fetch_cards()
            if len(cards) > card_count:
                self.schema_repository.replace_catalog()
                self.bulk_insert_repository.seed_cards(cards, source)
        return self.lookup_repository.get_summary()
