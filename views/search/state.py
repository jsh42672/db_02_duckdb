from __future__ import annotations

from dataclasses import dataclass

from domain.card.dto import CardDetailDTO


@dataclass(slots=True)
class SearchViewState:
    selected_card: CardDetailDTO | None = None
