from __future__ import annotations

import flet as ft


def card_image(src: str | None, width: int, height: int) -> ft.Control:
    if src:
        return ft.Image(src=src, width=width, height=height, fit=ft.BoxFit.CONTAIN)
    return ft.Container(width=width, height=height, bgcolor=ft.Colors.GREY_200)
