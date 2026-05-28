from __future__ import annotations

import flet as ft

from domain.card.dto import CardDetailDTO
from views.common.formatters import fmt, fmt_price


class SearchDetailPanel:
    def __init__(self, on_add_to_deck):
        self.on_add_to_deck = on_add_to_deck
        self.title = ft.Text("카드를 선택하세요", size=18, weight="bold")
        self.image_box = ft.Container(
            width=230,
            height=320,
            alignment=ft.Alignment.CENTER,
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=6,
            content=ft.Text("No image", color=ft.Colors.GREY_600),
        )
        self.actions = ft.Row(spacing=4, wrap=True)
        self.body = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)
        self.control = ft.Container(
            width=360,
            padding=12,
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            content=ft.Column(
                [self.title, self.image_box, self.actions, ft.Divider(height=1), self.body],
                expand=True,
                spacing=10,
            ),
        )

    def show_card(self, detail: CardDetailDTO) -> None:
        self.title.value = detail.name
        if detail.image_url:
            self.image_box.content = ft.Image(src=detail.image_url, width=220, height=310, fit=ft.BoxFit.CONTAIN)
        else:
            self.image_box.content = ft.Text("No image", color=ft.Colors.GREY_600)

        ban_text = ", ".join(f"{key}: {value}" for key, value in detail.bans.items()) or "No banlist status"
        set_controls = [
            ft.Text(
                f"{row.set_name} | {fmt(row.set_code)} | {fmt(row.rarity)} | {fmt_price(row.set_price)}",
                size=12,
            )
            for row in detail.sets[:8]
        ] or [ft.Text("No set data", size=12, color=ft.Colors.GREY_600)]
        self.body.controls = [
            ft.Text(detail.card_type, color=ft.Colors.BLUE_GREY_700),
            ft.Text(
                f"Attribute {fmt(detail.attribute)} | Race {fmt(detail.race)} | "
                f"Lv/Rank {fmt(detail.level)} | ATK {fmt(detail.atk)} | DEF {fmt(detail.def_)}",
                size=12,
            ),
            ft.Text(f"Archetype: {fmt(detail.archetypes)}", size=12),
            ft.Text(f"Banlist: {ban_text}", size=12, color=ft.Colors.RED_700),
            ft.Text(
                "Prices: "
                f"TCGPlayer {fmt_price(detail.prices.tcgplayer)}, "
                f"Cardmarket {fmt_price(detail.prices.cardmarket)}, "
                f"eBay {fmt_price(detail.prices.ebay)}, "
                f"Amazon {fmt_price(detail.prices.amazon)}",
                size=12,
            ),
            ft.Text(detail.description or "", size=12, selectable=True),
            ft.Divider(height=1),
            ft.Text("Card sets", weight="bold", size=13),
            *set_controls,
        ]
        self.actions.controls = [
            ft.OutlinedButton("Main", icon=ft.Icons.ADD, on_click=lambda e, dto=detail: self.on_add_to_deck(dto, "MAIN")),
            ft.OutlinedButton("Extra", icon=ft.Icons.PLAYLIST_ADD, on_click=lambda e, dto=detail: self.on_add_to_deck(dto, "EXTRA")),
            ft.OutlinedButton("Side", icon=ft.Icons.AUTO_FIX_HIGH, on_click=lambda e, dto=detail: self.on_add_to_deck(dto, "SIDE")),
        ]
