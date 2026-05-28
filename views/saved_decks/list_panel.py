from __future__ import annotations

import flet as ft


class SavedDeckListPanel:
    def __init__(self, on_show_deck, on_delete_deck, on_refresh):
        self.list_view = ft.ListView(width=340, spacing=6, expand=True)
        self.control = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Saved Decks", size=18, weight="bold"),
                        ft.IconButton(icon=ft.Icons.REFRESH, tooltip="새로고침", on_click=lambda e: on_refresh()),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                self.list_view,
            ],
            width=360,
            expand=False,
        )
        self.on_show_deck = on_show_deck
        self.on_delete_deck = on_delete_deck

    def set_decks(self, decks) -> None:
        if not decks:
            self.list_view.controls = [ft.Text("저장된 덱이 없습니다.", color=ft.Colors.GREY_600)]
            return
        self.list_view.controls = [
            ft.Container(
                padding=8,
                border=ft.Border.all(1, ft.Colors.GREY_300),
                border_radius=6,
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(deck.name, weight="bold"),
                                ft.Text(
                                    f"{deck.ban_format} | {deck.total_cards} cards | {deck.created_at}",
                                    size=12,
                                    color=ft.Colors.GREY_700,
                                ),
                            ],
                            expand=True,
                            spacing=2,
                        ),
                        ft.IconButton(icon=ft.Icons.INFO, tooltip="상세 조회", on_click=lambda e, deck_id=deck.id: self.on_show_deck(deck_id)),
                        ft.IconButton(icon=ft.Icons.DELETE, tooltip="삭제", on_click=lambda e, dto=deck: self.on_delete_deck(dto)),
                    ]
                ),
            )
            for deck in decks
        ]
