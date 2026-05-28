from __future__ import annotations

from typing import Protocol

from domain.card.dto import AppSummaryDTO, CardDetailDTO, CardSearchFilterDTO, CardSummaryDTO, LookupOptionsDTO
from domain.deck.dto import DeckItemDTO, SavedDeckDetailDTO, SavedDeckSummaryDTO
from domain.seed.dto import SeedCardDTO


class CardQueryRepository(Protocol):
    def search_cards(self, filters: CardSearchFilterDTO) -> list[CardSummaryDTO]:
        ...

    def card_count(self) -> int:
        ...


class CardDetailRepository(Protocol):
    def get_card_detail(self, card_id: int) -> CardDetailDTO | None:
        ...


class LookupRepository(Protocol):
    def get_lookup_options(self) -> LookupOptionsDTO:
        ...

    def get_summary(self) -> AppSummaryDTO:
        ...


class DeckCommandRepository(Protocol):
    def save_deck(self, name: str, memo: str, ban_format: str, items: list[DeckItemDTO]) -> int:
        ...

    def delete_deck(self, deck_id: int) -> None:
        ...


class DeckQueryRepository(Protocol):
    def list_decks(self) -> list[SavedDeckSummaryDTO]:
        ...

    def get_deck_detail(self, deck_id: int) -> SavedDeckDetailDTO | None:
        ...

    def deck_count(self) -> int:
        ...


class DeckValidationRepository(Protocol):
    def get_validation_card_map(self, card_ids: list[int]) -> dict[int, dict[str, object]]:
        ...

    def get_ban_status_map(self, card_ids: list[int], ban_format: str) -> dict[int, str]:
        ...

    def get_legal_candidates(self, extra_deck: bool, ban_format: str, limit: int = 200) -> list[dict[str, object]]:
        ...


class SeedSchemaRepository(Protocol):
    def apply_schema(self) -> None:
        ...

    def replace_catalog(self) -> None:
        ...


class SeedMetaRepository(Protocol):
    def get_meta_value(self, key: str) -> str | None:
        ...

    def set_meta_value(self, key: str, value: str) -> None:
        ...


class SeedBulkInsertRepository(Protocol):
    def seed_cards(self, cards: list[SeedCardDTO], source: str) -> None:
        ...
