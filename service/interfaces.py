from __future__ import annotations

from typing import Protocol

from domain.card.dto import AppSummaryDTO, CardDetailDTO, CardSearchFilterDTO, CardSummaryDTO, LookupOptionsDTO
from domain.deck.dto import DeckItemDTO, DeckValidationResultDTO, SavedDeckDetailDTO, SavedDeckSummaryDTO, SaveDeckRequestDTO


class CardSearchService(Protocol):
    def search(self, filters: CardSearchFilterDTO) -> list[CardSummaryDTO]:
        ...


class CardDetailService(Protocol):
    def get(self, card_id: int) -> CardDetailDTO | None:
        ...


class LookupService(Protocol):
    def options(self) -> LookupOptionsDTO:
        ...


class DeckValidationService(Protocol):
    def validate(self, items: list[DeckItemDTO], ban_format: str) -> DeckValidationResultDTO:
        ...


class SavedDeckService(Protocol):
    def save(self, request: SaveDeckRequestDTO) -> int:
        ...

    def list(self) -> list[SavedDeckSummaryDTO]:
        ...

    def detail(self, deck_id: int) -> SavedDeckDetailDTO | None:
        ...

    def delete(self, deck_id: int) -> None:
        ...


class InitializeService(Protocol):
    def initialize(self) -> AppSummaryDTO:
        ...
