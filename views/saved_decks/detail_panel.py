from __future__ import annotations

import flet as ft

from domain.deck.constants import SECTION_LABELS, SECTIONS


class SavedDeckDetailPanel:
    def __init__(self):
        self.control = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    def show_empty(self) -> None:
        self.control.controls = [ft.Text("덱을 저장하면 이곳에서 조회할 수 있습니다.")]

    def show_deck(self, detail, validation_result) -> None:
        controls = [
            ft.Text(detail.name, size=20, weight="bold"),
            ft.Text(f"Format: {detail.ban_format} | Created: {detail.created_at}", size=12),
            ft.Text(detail.memo or "", size=12, color=ft.Colors.GREY_700),
            ft.Text(
                "\n".join(validation_result.messages[:8]),
                size=12,
                color=ft.Colors.GREEN_700 if validation_result.ok else ft.Colors.RED_700,
            ),
            ft.Divider(height=1),
        ]
        for section in SECTIONS:
            section_rows = [row for row in detail.cards if row.section == section]
            controls.append(ft.Text(f"{SECTION_LABELS[section]} Deck", weight="bold"))
            if not section_rows:
                controls.append(ft.Text("없음", size=12, color=ft.Colors.GREY_600))
            for row in section_rows:
                ban = f" | {row.ban_status}" if row.ban_status else ""
                controls.append(ft.Text(f"x{row.quantity} {row.name} ({row.card_type}{ban})", size=12))
        self.control.controls = controls
