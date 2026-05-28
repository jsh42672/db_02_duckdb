from __future__ import annotations

from domain.card.dto import AppSummaryDTO


class DefaultInitializeService:
    def __init__(
        self,
        provider,
        card_query_repository,
        deck_query_repository,
        lookup_repository,
        schema_repository,
        meta_repository,
        bulk_insert_repository,
    ):
        self.provider = provider
        self.card_query_repository = card_query_repository
        self.deck_query_repository = deck_query_repository
        self.lookup_repository = lookup_repository
        self.schema_repository = schema_repository
        self.meta_repository = meta_repository
        self.bulk_insert_repository = bulk_insert_repository

    def initialize(self) -> AppSummaryDTO:
        self.schema_repository.apply_schema()
        card_count = self.card_query_repository.card_count()
        seed_source = self.meta_repository.get_meta_value("seed_source")
        if card_count == 0:
            cards, source = self.provider.fetch_cards()
            self.bulk_insert_repository.seed_cards(cards, source)
        elif seed_source == "fallback" and self.deck_query_repository.deck_count() == 0:
            cards, source = self.provider.fetch_cards()
            if len(cards) > card_count:
                self.schema_repository.replace_catalog()
                self.bulk_insert_repository.seed_cards(cards, source)
        return self.lookup_repository.get_summary()
