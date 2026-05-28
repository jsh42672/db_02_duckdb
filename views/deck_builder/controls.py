from __future__ import annotations

import flet as ft

from domain.deck.constants import BAN_FORMATS


class DeckBuilderControls:
    def __init__(self, on_validate, on_save, on_sample, on_clear):
        self.deck_name = ft.TextField(label="Deck name", value="My YGO Deck", width=260)
        self.deck_memo = ft.TextField(label="Memo", multiline=True, min_lines=2, max_lines=3)
        self.ban_format = ft.Dropdown(
            label="Ban format",
            value="TCG",
            width=130,
            options=[ft.dropdown.Option(key=value, text=value) for value in BAN_FORMATS],
            on_select=lambda e: on_validate(),
        )
        self.deck_count_text = ft.Text(size=13, color=ft.Colors.GREY_700)
        self.validation_text = ft.Text(size=13, color=ft.Colors.GREY_800, selectable=True)
        self.actions = ft.Row(
            [
                self.deck_name,
                self.ban_format,
                ft.FilledButton("Validate", icon=ft.Icons.CHECK, on_click=on_validate),
                ft.FilledButton("Save", icon=ft.Icons.SAVE, on_click=on_save),
                ft.OutlinedButton("Sample", icon=ft.Icons.AUTO_FIX_HIGH, on_click=on_sample),
                ft.OutlinedButton("Clear", icon=ft.Icons.CLEAR, on_click=on_clear),
            ],
            wrap=True,
            spacing=8,
        )
