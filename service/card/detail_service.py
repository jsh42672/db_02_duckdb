from __future__ import annotations

from domain.card.dto import CardDetailDTO
from repository.interfaces import ICardDetailRepository


class DefaultCardDetailService:
    def __init__(self, repository: ICardDetailRepository):
        self.repository = repository

    def get(self, card_id: int) -> CardDetailDTO | None:
        return self.repository.get_card_detail(card_id)
