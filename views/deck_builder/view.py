from __future__ import annotations

import flet as ft

from domain.deck.dto import DeckItemDTO, SaveDeckRequestDTO
from views.deck_builder.controls import DeckBuilderControls
from views.deck_builder.deck_columns import DeckColumns
from views.deck_builder.state import DeckBuilderState


class DeckBuilderView:
    def __init__(self, page: ft.Page, detail_service, deck_builder_service, deck_validation_service, saved_deck_service, show_snack, on_deck_saved):
        self.page = page
        self.detail_service = detail_service
        self.deck_builder_service = deck_builder_service
        self.deck_validation_service = deck_validation_service
        self.saved_deck_service = saved_deck_service
        self.show_snack = show_snack
        self.on_deck_saved = on_deck_saved
        self.state = DeckBuilderState()

        self.controls = DeckBuilderControls(self.validate_current_deck, self.save_current_deck, self.fill_sample_deck, self.clear_deck)
        self.deck_columns = DeckColumns(self.change_quantity, self.remove_card)
        self.columns_row, _ = self.deck_columns.render(self.state.deck_items)
        self.control = ft.Column(
            [
                self.controls.actions,
                self.controls.deck_memo,
                self.controls.deck_count_text,
                self.controls.validation_text,
                self.columns_row,
            ],
            expand=True,
            spacing=8,
        )
        self.render_deck()

    def _to_deck_item(self, card, section: str, quantity: int = 1) -> DeckItemDTO:
        return DeckItemDTO(
            card_id=int(getattr(card, "id")),
            section=section,
            quantity=quantity,
            name=str(getattr(card, "name", "")),
            card_type=str(getattr(card, "card_type", "")),
            is_extra_deck=bool(getattr(card, "is_extra_deck", False)),
        )

    def add_card(self, card, section: str) -> None:
        is_extra = bool(getattr(card, "is_extra_deck", False))
        if section == "MAIN" and is_extra:
            self.show_snack("Extra Deck 몬스터는 Main Deck에 넣을 수 없습니다.", True)
            return
        if section == "EXTRA" and not is_extra:
            self.show_snack("Extra Deck에는 Fusion/Synchro/XYZ/Link 카드만 넣을 수 있습니다.", True)
            return

        card_id = int(getattr(card, "id"))
        section_cards = self.state.deck_items[section]
        if card_id not in section_cards:
            section_cards[card_id] = self._to_deck_item(card, section, 0)
        if section_cards[card_id].quantity >= 3:
            self.show_snack("같은 섹션에는 최대 3장까지 추가할 수 있습니다.", True)
            return
        section_cards[card_id].quantity += 1
        self.render_deck()

    def flatten_deck(self) -> list[DeckItemDTO]:
        rows: list[DeckItemDTO] = []
        for cards in self.state.deck_items.values():
            rows.extend(cards.values())
        return rows

    def change_quantity(self, section: str, card_id: int, delta: int) -> None:
        item = self.state.deck_items[section].get(card_id)
        if not item:
            return
        item.quantity += delta
        if item.quantity <= 0:
            del self.state.deck_items[section][card_id]
        elif item.quantity > 3:
            item.quantity = 3
            self.show_snack("카드별 최대 3장까지 가능합니다.", True)
        self.render_deck()

    def remove_card(self, section: str, card_id: int) -> None:
        self.state.deck_items[section].pop(card_id, None)
        self.render_deck()

    def render_deck(self) -> None:
        new_row, totals = self.deck_columns.render(self.state.deck_items)
        self.control.controls[-1] = new_row
        self.columns_row = new_row
        self.controls.deck_count_text.value = f"Main {totals['MAIN']} / Extra {totals['EXTRA']} / Side {totals['SIDE']}"
        self.page.update()

    def validate_current_deck(self, e=None) -> bool:
        result = self.deck_validation_service.validate(self.flatten_deck(), self.controls.ban_format.value or "TCG")
        self.controls.validation_text.value = "\n".join(result.messages[:10])
        self.controls.validation_text.color = ft.Colors.GREEN_700 if result.ok else ft.Colors.RED_700
        self.page.update()
        return result.ok

    def save_current_deck(self, e=None) -> None:
        name = (self.controls.deck_name.value or "").strip()
        if not name:
            self.show_snack("덱 이름을 입력하세요.", True)
            return
        try:
            deck_id = self.saved_deck_service.save(
                SaveDeckRequestDTO(
                    name=name,
                    memo=self.controls.deck_memo.value or "",
                    ban_format=self.controls.ban_format.value or "TCG",
                    items=self.flatten_deck(),
                )
            )
        except ValueError as exc:
            self.controls.validation_text.value = str(exc)
            self.controls.validation_text.color = ft.Colors.RED_700
            self.page.update()
            return
        self.on_deck_saved()
        self.show_snack(f"덱 저장 완료: #{deck_id}")

    def clear_deck(self, e=None) -> None:
        for section in self.state.deck_items:
            self.state.deck_items[section].clear()
        self.controls.validation_text.value = ""
        self.render_deck()

    def fill_sample_deck(self, e=None) -> None:
        rows = self.deck_builder_service.sample_deck_items(self.controls.ban_format.value or "TCG")
        if not rows:
            self.show_snack("샘플 덱을 만들 카드가 부족합니다.", True)
            return
        for section in self.state.deck_items:
            self.state.deck_items[section].clear()
        for row in rows:
            self.state.deck_items[row.section][row.card_id] = row
        self.render_deck()
        self.validate_current_deck()
