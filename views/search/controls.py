from __future__ import annotations

import flet as ft

from domain.card.dto import LookupOptionsDTO
from views.common.formatters import option_items


class SearchControls:
    def __init__(self, options: LookupOptionsDTO, on_search, on_reset):
        self.keyword_input = ft.TextField(
            label="Card name / effect text",
            prefix_icon=ft.Icons.SEARCH,
            width=280,
            on_submit=lambda e: on_search(),
        )
        self.type_filter = ft.Dropdown(label="Type", width=220, options=option_items(options.card_type))
        self.attribute_filter = ft.Dropdown(label="Attribute", width=150, options=option_items(options.attribute))
        self.race_filter = ft.Dropdown(label="Race", width=180, options=option_items(options.race))
        self.archetype_filter = ft.Dropdown(label="Archetype", width=220, options=option_items(options.archetype))
        self.level_filter = ft.TextField(label="Lv/Rank", width=90)
        self.atk_min_filter = ft.TextField(label="ATK min", width=100)
        self.atk_max_filter = ft.TextField(label="ATK max", width=100)
        self.def_min_filter = ft.TextField(label="DEF min", width=100)
        self.def_max_filter = ft.TextField(label="DEF max", width=100)
        self.result_count = ft.Text("검색 결과 0장", size=13, color=ft.Colors.GREY_700)
        self.control = ft.Column(
            [
                ft.Row(
                    [
                        self.keyword_input,
                        self.type_filter,
                        self.attribute_filter,
                        self.race_filter,
                        self.archetype_filter,
                    ],
                    wrap=True,
                    spacing=8,
                ),
                ft.Row(
                    [
                        self.level_filter,
                        self.atk_min_filter,
                        self.atk_max_filter,
                        self.def_min_filter,
                        self.def_max_filter,
                        ft.FilledButton("Search", icon=ft.Icons.SEARCH, on_click=on_search),
                        ft.OutlinedButton("Reset", icon=ft.Icons.CLEAR, on_click=on_reset),
                    ],
                    wrap=True,
                    spacing=8,
                ),
            ],
            spacing=8,
        )

    def reset(self) -> None:
        for control in (
            self.keyword_input,
            self.level_filter,
            self.atk_min_filter,
            self.atk_max_filter,
            self.def_min_filter,
            self.def_max_filter,
        ):
            control.value = ""
        for control in (self.type_filter, self.attribute_filter, self.race_filter, self.archetype_filter):
            control.value = ""
