from __future__ import annotations

from typing import Protocol

from domain.seed.dto import SeedCardDTO


class CardDataProvider(Protocol):
    def fetch_cards(self) -> tuple[list[SeedCardDTO], str]:
        ...
