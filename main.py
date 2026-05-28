import flet as ft

from app import build_app_container
from views import DeckBuilderView, SavedDecksView, SearchView
from views.common.dialogs import build_delete_dialog, show_snack


def main(page: ft.Page):
    page.title = "YGO Deck Lab"
    page.padding = 16
    page.window.width = 1180
    page.window.height = 760
    page.theme_mode = ft.ThemeMode.LIGHT

    container = build_app_container()

    loading = ft.Column(
        [
            ft.ProgressRing(),
            ft.Text("DuckDB initializing and loading card data...", size=16),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True,
    )
    page.add(loading)
    page.update()

    summary = container.initialize_service.initialize()
    page.clean()

    snack = ft.SnackBar(content=ft.Text(""))
    delete_dialog = build_delete_dialog()
    page.overlay.extend([snack, delete_dialog])

    def show_message(message: str, is_error: bool = False) -> None:
        show_snack(page, snack, message, is_error)

    summary_text = ft.Text(
        f"cards {summary.cards:,} | archetypes {summary.archetypes:,} | "
        f"sets {summary.sets:,} | source {summary.source}",
        size=12,
        color=ft.Colors.GREY_700,
    )
    header = ft.Row(
        [
            ft.Column(
                [
                    ft.Text("YGO Deck Lab", size=28, weight="bold"),
                    summary_text,
                ],
                spacing=2,
            ),
            ft.Text("Flet + DuckDB", size=14, color=ft.Colors.BLUE_GREY_600),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    saved_decks_view = SavedDecksView(
        page=page,
        saved_deck_service=container.saved_deck_service,
        deck_validation_service=container.deck_validation_service,
        show_snack=show_message,
        delete_dialog=delete_dialog,
    )
    deck_builder_view = DeckBuilderView(
        page=page,
        detail_service=container.detail_service,
        deck_builder_service=container.deck_builder_service,
        deck_validation_service=container.deck_validation_service,
        saved_deck_service=container.saved_deck_service,
        show_snack=show_message,
        on_deck_saved=saved_decks_view.refresh_decks,
    )
    search_view = SearchView(
        page=page,
        search_service=container.search_service,
        detail_service=container.detail_service,
        lookup_service=container.lookup_service,
        on_add_to_deck=deck_builder_view.add_card,
        show_snack=show_message,
    )

    view_host = ft.Container(content=search_view.control, expand=True)

    def show_view(view_name: str) -> None:
        if view_name == "search":
            view_host.content = search_view.control
        elif view_name == "deck":
            view_host.content = deck_builder_view.control
        else:
            saved_decks_view.refresh_decks()
            view_host.content = saved_decks_view.control
        page.update()

    navigation = ft.Row(
        [
            ft.FilledButton("카드 검색", icon=ft.Icons.SEARCH, on_click=lambda e: show_view("search")),
            ft.OutlinedButton("덱 빌더", icon=ft.Icons.ADD, on_click=lambda e: show_view("deck")),
            ft.OutlinedButton("저장된 덱", icon=ft.Icons.INFO, on_click=lambda e: show_view("saved")),
        ],
        spacing=8,
    )

    page.add(header, navigation, ft.Divider(height=1), view_host)
    saved_decks_view.refresh_decks()
    search_view.perform_search()


if __name__ == "__main__":
    ft.run(main)
