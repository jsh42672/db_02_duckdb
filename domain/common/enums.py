from __future__ import annotations

from enum import StrEnum


class DeckSection(StrEnum):
    MAIN = "MAIN"
    EXTRA = "EXTRA"
    SIDE = "SIDE"


class BanFormat(StrEnum):
    TCG = "TCG"
    OCG = "OCG"
    GOAT = "GOAT"
