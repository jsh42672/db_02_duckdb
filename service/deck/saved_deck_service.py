from __future__ import annotations

from domain.deck.dto import SavedDeckDetailDTO, SavedDeckSummaryDTO, SaveDeckRequestDTO
from repository.interfaces import IDeckCommandRepository, IDeckQueryRepository
from service.deck.validation_service import DefaultDeckValidationService


class DefaultSavedDeckService:
    def __init__(
        self,
        command_repository: IDeckCommandRepository,
        query_repository: IDeckQueryRepository,
        validation_service: DefaultDeckValidationService,
    ):
        self.command_repository = command_repository
        self.query_repository = query_repository
        self.validation_service = validation_service

    def save(self, request: SaveDeckRequestDTO) -> int:
        result = self.validation_service.validate(request.items, request.ban_format)
        if not result.ok:
            raise ValueError("\n".join(result.messages))
        return self.command_repository.save_deck(
            request.name,
            request.memo,
            request.ban_format,
            request.items,
        )

    def list(self) -> list[SavedDeckSummaryDTO]:
        return self.query_repository.list_decks()

    def detail(self, deck_id: int) -> SavedDeckDetailDTO | None:
        return self.query_repository.get_deck_detail(deck_id)

    def delete(self, deck_id: int) -> None:
        self.command_repository.delete_deck(deck_id)
