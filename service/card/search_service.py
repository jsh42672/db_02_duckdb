from __future__ import annotations

from domain.card.dto import CardSearchFilterDTO, CardSummaryDTO
from repository.interfaces import ICardQueryRepository


class DefaultCardSearchService:
    def __init__(self, repository: ICardQueryRepository):
        self.repository = repository

    def search(self, filters: CardSearchFilterDTO) -> list[CardSummaryDTO]:
        return self.repository.search_cards(filters)
