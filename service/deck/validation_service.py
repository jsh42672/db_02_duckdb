from __future__ import annotations

from domain.deck.dto import DeckItemDTO, DeckValidationResultDTO
from domain.deck.rules import result_from_messages, status_to_limit, validate_deck_size


class DefaultDeckValidationService:
    def __init__(self, repository):
        self.repository = repository

    def validate(self, items: list[DeckItemDTO], ban_format: str) -> DeckValidationResultDTO:
        if not items:
            return DeckValidationResultDTO(ok=False, messages=["Deck is empty."])

        card_ids = sorted({int(item.card_id) for item in items})
        cards = self.repository.get_validation_card_map(card_ids)
        bans = self.repository.get_ban_status_map(card_ids, ban_format)

        messages: list[str] = []
        card_quantities: dict[int, int] = {}

        for item in items:
            card_quantities[item.card_id] = card_quantities.get(item.card_id, 0) + item.quantity
            card = cards.get(item.card_id)
            if not card:
                messages.append(f"Unknown card id: {item.card_id}")
                continue
            if card["is_extra_deck"] and item.section == "MAIN":
                messages.append(f"{card['name']} must be placed in the Extra Deck.")
            if not card["is_extra_deck"] and item.section == "EXTRA":
                messages.append(f"{card['name']} cannot be placed in the Extra Deck.")

        messages.extend(validate_deck_size(items))

        for card_id, quantity in card_quantities.items():
            status = bans.get(card_id)
            limit = status_to_limit(status)
            if quantity > limit:
                name = str(cards.get(card_id, {}).get("name", card_id))
                status_text = status or "Unlimited"
                messages.append(f"{name}: {quantity} copies exceeds {ban_format} {status_text} limit.")

        return result_from_messages(messages)
