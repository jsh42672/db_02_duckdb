from __future__ import annotations

from domain.card.dto import LookupOptionsDTO
from repository.interfaces import ILookupRepository


class DefaultLookupService:
    def __init__(self, repository: ILookupRepository):
        self.repository = repository

    def options(self) -> LookupOptionsDTO:
        return self.repository.get_lookup_options()
