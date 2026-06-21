from __future__ import annotations

import flet as ft

from domain.deck.dto import DeckItemDTO
from views.saved_decks.detail_panel import SavedDeckDetailPanel
from views.saved_decks.list_panel import SavedDeckListPanel
from views.saved_decks.state import SavedDecksState


class SavedDecksView:
    def __init__(self, page: ft.Page, saved_deck_service, deck_validation_service, show_snack, delete_dialog: ft.AlertDialog):
        self.page = page
        self.saved_deck_service = saved_deck_service
        self.deck_validation_service = deck_validation_service
        self.show_snack = show_snack
        self.delete_dialog = delete_dialog
        self.state = SavedDecksState()

        self.list_panel = SavedDeckListPanel(self.show_saved_deck, self.ask_delete_deck, self.refresh_decks)
        self.detail_panel = SavedDeckDetailPanel()
        self.detail_panel.show_empty()
        self.control = ft.Row(
            [self.list_panel.control, ft.VerticalDivider(width=1), self.detail_panel.control],
            expand=True,
        )

    def refresh_decks(self) -> None:
        # 저장·삭제 이후 같은 메서드를 호출해 목록과 빈 상세 패널을 일관되게 갱신한다.
        decks = self.saved_deck_service.list()
        self.list_panel.set_decks(decks)
        if not decks:
            self.detail_panel.show_empty()
        self.page.update()

    def show_saved_deck(self, deck_id: int) -> None:
        detail = self.saved_deck_service.detail(int(deck_id))
        if detail is None:
            self.show_snack("덱을 찾을 수 없습니다.", True)
            return
        # 저장 시점 이후 규칙이 달라질 수 있으므로 상세 조회 때 현재 규칙으로 다시 검증한다.
        result = self.deck_validation_service.validate(
            [
                DeckItemDTO(card_id=row.card_id, section=row.section, quantity=row.quantity)
                for row in detail.cards
            ],
            detail.ban_format,
        )
        self.state.selected_deck_id = deck_id
        self.detail_panel.show_deck(detail, result)
        self.page.update()

    def ask_delete_deck(self, deck) -> None:
        # 실제 삭제는 사용자가 확인 대화상자의 삭제 버튼을 눌렀을 때만 수행한다.
        def close_dialog(e=None):
            self.delete_dialog.open = False
            self.page.update()

        def delete_now(e=None):
            self.saved_deck_service.delete(int(deck.id))
            close_dialog()
            self.refresh_decks()
            self.show_snack(f"덱 삭제 완료: {deck.name}")

        self.delete_dialog.title = ft.Text("덱 삭제")
        self.delete_dialog.content = ft.Text(f"'{deck.name}' 덱을 삭제할까요?")
        self.delete_dialog.actions = [
            ft.TextButton("취소", on_click=close_dialog),
            ft.FilledButton("삭제", icon=ft.Icons.DELETE, on_click=delete_now),
        ]
        self.delete_dialog.open = True
        self.page.update()
