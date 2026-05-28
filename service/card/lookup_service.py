from __future__ import annotations

from domain.card.dto import LookupOptionsDTO


class DefaultLookupService:
    def __init__(self, repository):
        self.repository = repository

    def options(self) -> LookupOptionsDTO:
        return self.repository.get_lookup_options()
