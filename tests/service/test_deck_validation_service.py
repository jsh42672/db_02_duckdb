from __future__ import annotations

import unittest

from domain.deck.dto import DeckItemDTO
from service.deck.validation_service import DefaultDeckValidationService


class StubDeckValidationRepository:
    def get_validation_card_map(self, card_ids: list[int]) -> dict[int, dict[str, object]]:
        return {
            1: {"name": "Main Card", "is_extra_deck": False},
            2: {"name": "Extra Card", "is_extra_deck": True},
            3: {"name": "Limited Card", "is_extra_deck": False},
        }

    def get_ban_status_map(self, card_ids: list[int], ban_format: str) -> dict[int, str]:
        return {3: "Limited"}

    def get_legal_candidates(self, extra_deck: bool, ban_format: str, limit: int = 200) -> list[dict[str, object]]:
        return []


class TestDeckValidationService(unittest.TestCase):
    def setUp(self) -> None:
        self.service = DefaultDeckValidationService(StubDeckValidationRepository())

    def test_reports_empty_deck(self) -> None:
        result = self.service.validate([], "TCG")
        self.assertFalse(result.ok)
        self.assertEqual(["Deck is empty."], result.messages)

    def test_reports_size_and_limit_violations(self) -> None:
        result = self.service.validate(
            [
                DeckItemDTO(card_id=3, section="MAIN", quantity=2),
                DeckItemDTO(card_id=2, section="MAIN", quantity=1),
            ],
            "TCG",
        )
        self.assertFalse(result.ok)
        self.assertTrue(any("Limited Card" in message for message in result.messages))
        self.assertTrue(any("Extra Deck" in message for message in result.messages))
        self.assertTrue(any("Main Deck must contain 40 to 60 cards." == message for message in result.messages))


if __name__ == "__main__":
    unittest.main()
