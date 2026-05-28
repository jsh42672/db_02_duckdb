from __future__ import annotations

from domain.card.dto import CardSearchFilterDTO, CardSummaryDTO


class DefaultCardSearchService:
    def __init__(self, repository):
        self.repository = repository

    def search(self, filters: CardSearchFilterDTO) -> list[CardSummaryDTO]:
        return self.repository.search_cards(filters)
