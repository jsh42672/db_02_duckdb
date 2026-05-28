from __future__ import annotations

from domain.deck.dto import DeckItemDTO
from domain.deck.rules import status_to_limit


class DefaultDeckBuilderService:
    def __init__(self, validation_repository, detail_service):
        self.validation_repository = validation_repository
        self.detail_service = detail_service

    def sample_deck_items(self, ban_format: str) -> list[DeckItemDTO]:
        main_candidates = self.validation_repository.get_legal_candidates(False, ban_format)
        extra_candidates = self.validation_repository.get_legal_candidates(True, ban_format)

        items: list[DeckItemDTO] = []
        main_count = 0
        for candidate in main_candidates:
            if main_count >= 40:
                break
            limit = status_to_limit(candidate["status"])
            quantity = min(limit, 3, 40 - main_count)
            if quantity <= 0:
                continue
            detail = self.detail_service.get(int(candidate["id"]))
            items.append(
                DeckItemDTO(
                    card_id=int(candidate["id"]),
                    section="MAIN",
                    quantity=quantity,
                    name=str(candidate["name"]),
                    card_type=detail.card_type if detail else "",
                    is_extra_deck=bool(detail.is_extra_deck) if detail else False,
                )
            )
            main_count += quantity

        for candidate in extra_candidates[:5]:
            detail = self.detail_service.get(int(candidate["id"]))
            items.append(
                DeckItemDTO(
                    card_id=int(candidate["id"]),
                    section="EXTRA",
                    quantity=1,
                    name=str(candidate["name"]),
                    card_type=detail.card_type if detail else "",
                    is_extra_deck=bool(detail.is_extra_deck) if detail else True,
                )
            )
        return items
