from __future__ import annotations

import flet as ft


def fmt(value) -> str:
    return "-" if value is None or value == "" else str(value)


def fmt_price(value) -> str:
    if value is None:
        return "-"
    return f"${float(value):.2f}"


def option_items(values: list[str]) -> list[ft.dropdown.Option]:
    return [ft.dropdown.Option(key="", text="All")] + [
        ft.dropdown.Option(key=value, text=value) for value in values
    ]
