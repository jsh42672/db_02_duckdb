from __future__ import annotations

import flet as ft

from domain.deck.constants import SECTION_LABELS, SECTIONS
from domain.deck.dto import DeckItemDTO


class DeckColumns:
    def __init__(self, on_change_quantity, on_remove_card):
        self.columns = {
            section: ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, expand=True)
            for section in SECTIONS
        }
        self.on_change_quantity = on_change_quantity
        self.on_remove_card = on_remove_card

    def render(self, deck_items: dict[str, dict[int, DeckItemDTO]]) -> tuple[ft.Row, dict[str, int]]:
        totals = {section: 0 for section in SECTIONS}
        for section in SECTIONS:
            rows = []
            for item in sorted(deck_items[section].values(), key=lambda x: x.name):
                totals[section] += item.quantity
                rows.append(
                    ft.Container(
                        padding=6,
                        border=ft.Border.all(1, ft.Colors.GREY_300),
                        border_radius=6,
                        content=ft.Row(
                            [
                                ft.Text(item.name, expand=True, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Text(f"x{item.quantity}", width=34, text_align=ft.TextAlign.CENTER),
                                ft.IconButton(icon=ft.Icons.REMOVE, tooltip="수량 감소", on_click=lambda e, section=section, card_id=item.card_id: self.on_change_quantity(section, card_id, -1)),
                                ft.IconButton(icon=ft.Icons.ADD, tooltip="수량 증가", on_click=lambda e, section=section, card_id=item.card_id: self.on_change_quantity(section, card_id, 1)),
                                ft.IconButton(icon=ft.Icons.DELETE, tooltip="삭제", on_click=lambda e, section=section, card_id=item.card_id: self.on_remove_card(section, card_id)),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    )
                )
            self.columns[section].controls = [ft.Text(f"{SECTION_LABELS[section]} Deck ({totals[section]})", weight="bold"), *rows]

        row = ft.Row(
            [
                ft.Container(self.columns["MAIN"], expand=2, padding=8, border=ft.Border.all(1, ft.Colors.GREY_300), border_radius=8),
                ft.Container(self.columns["EXTRA"], expand=1, padding=8, border=ft.Border.all(1, ft.Colors.GREY_300), border_radius=8),
                ft.Container(self.columns["SIDE"], expand=1, padding=8, border=ft.Border.all(1, ft.Colors.GREY_300), border_radius=8),
            ],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        return row, totals
