from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SavedDecksState:
    selected_deck_id: int | None = None
