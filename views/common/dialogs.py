from __future__ import annotations

import flet as ft


def show_snack(page: ft.Page, snack_bar: ft.SnackBar, message: str, is_error: bool = False) -> None:
    snack_bar.content = ft.Text(message)
    snack_bar.bgcolor = ft.Colors.RED_400 if is_error else ft.Colors.GREEN_500
    snack_bar.open = True
    page.update()


def build_delete_dialog() -> ft.AlertDialog:
    return ft.AlertDialog(
        modal=True,
        title=ft.Text(""),
        content=ft.Text(""),
        actions=[],
    )
