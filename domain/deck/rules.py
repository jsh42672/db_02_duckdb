from __future__ import annotations

from domain.deck.constants import SECTIONS
from domain.deck.dto import DeckItemDTO, DeckValidationResultDTO


def status_to_limit(status: str | None) -> int:
    # API가 반환하는 영문 금지 제한 상태를 실제 투입 가능 수량으로 변환한다.
    if not status:
        return 3
    normalized = status.lower()
    if "forbidden" in normalized or "banned" in normalized:
        return 0
    if "semi" in normalized:
        return 2
    if "limited" in normalized:
        return 1
    return 3


def empty_deck_totals() -> dict[str, int]:
    return {section: 0 for section in SECTIONS}


def validate_deck_size(items: list[DeckItemDTO]) -> list[str]:
    # 동일 카드 제한과 별개로 Main/Extra/Side의 전체 장수 규칙을 검사한다.
    totals = empty_deck_totals()
    for item in items:
        totals[item.section] += item.quantity

    messages: list[str] = []
    if not 40 <= totals["MAIN"] <= 60:
        messages.append("Main Deck must contain 40 to 60 cards.")
    if not 0 <= totals["EXTRA"] <= 15:
        messages.append("Extra Deck must contain 0 to 15 cards.")
    if not 0 <= totals["SIDE"] <= 15:
        messages.append("Side Deck must contain 0 to 15 cards.")
    return messages


def result_from_messages(messages: list[str]) -> DeckValidationResultDTO:
    return DeckValidationResultDTO(
        ok=not messages,
        messages=messages or ["Deck is legal."],
    )
