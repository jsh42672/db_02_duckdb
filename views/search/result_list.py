from __future__ import annotations

import flet as ft

from domain.card.dto import CardSummaryDTO
from views.common.formatters import fmt
from views.common.widgets import card_image


class SearchResultList:
    def __init__(self):
        self.list_view = ft.ListView(expand=True, spacing=6, auto_scroll=False)

    def set_cards(self, cards: list[CardSummaryDTO], on_select, on_add_to_deck) -> None:
        self.list_view.controls = [self._card_line(card, on_select, on_add_to_deck) for card in cards]

    def _card_line(self, card: CardSummaryDTO, on_select, on_add_to_deck) -> ft.Control:
        stats = (
            f"{fmt(card.attribute)} / {fmt(card.race)} / "
            f"Lv {fmt(card.level)} / ATK {fmt(card.atk)} / DEF {fmt(card.def_)}"
        )
        return ft.Container(
            padding=8,
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=6,
            on_click=lambda e, card_id=card.id: on_select(card_id),
            content=ft.Row(
                [
                    card_image(card.image_small, 46, 64),
                    ft.Column(
                        [
                            ft.Text(card.name, weight="bold", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(card.card_type, size=12, color=ft.Colors.BLUE_GREY_700),
                            ft.Text(stats, size=12, color=ft.Colors.GREY_700),
                            ft.Text(fmt(card.archetypes), size=12, color=ft.Colors.GREY_600),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.IconButton(icon=ft.Icons.INFO, tooltip="상세 보기", on_click=lambda e, card_id=card.id: on_select(card_id)),
                    ft.IconButton(icon=ft.Icons.ADD, tooltip="Main Deck에 추가", on_click=lambda e, dto=card: on_add_to_deck(dto, "MAIN")),
                    ft.IconButton(icon=ft.Icons.PLAYLIST_ADD, tooltip="Extra Deck에 추가", on_click=lambda e, dto=card: on_add_to_deck(dto, "EXTRA")),
                    ft.IconButton(icon=ft.Icons.AUTO_FIX_HIGH, tooltip="Side Deck에 추가", on_click=lambda e, dto=card: on_add_to_deck(dto, "SIDE")),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )
