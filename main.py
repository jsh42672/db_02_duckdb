import flet as ft

from ygo_db import BAN_FORMATS, SECTIONS, YgoRepository


SECTION_LABELS = {
    "MAIN": "Main",
    "EXTRA": "Extra",
    "SIDE": "Side",
}


def fmt(value):
    return "-" if value is None or value == "" else str(value)


def fmt_price(value):
    if value is None:
        return "-"
    return f"${float(value):.2f}"


def option_items(values):
    return [ft.dropdown.Option(key="", text="All")] + [
        ft.dropdown.Option(key=value, text=value) for value in values
    ]


def main(page: ft.Page):
    page.title = "YGO Deck Lab"
    page.padding = 16
    page.window.width = 1180
    page.window.height = 760
    page.theme_mode = ft.ThemeMode.LIGHT

    repo = YgoRepository()

    loading = ft.Column(
        [
            ft.ProgressRing(),
            ft.Text("DuckDB 초기화 및 카드 데이터 준비 중...", size=16),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True,
    )
    page.add(loading)
    page.update()

    summary = repo.initialize()
    options = repo.options()
    page.clean()

    snack = ft.SnackBar(content=ft.Text(""))
    delete_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(""),
        content=ft.Text(""),
        actions=[],
    )
    page.overlay.extend([snack, delete_dialog])

    deck_items = {section: {} for section in SECTIONS}
    selected_detail = {"card": None}

    def show_snack(message, is_error=False):
        snack.content = ft.Text(message)
        snack.bgcolor = ft.Colors.RED_400 if is_error else ft.Colors.GREEN_500
        snack.open = True
        page.update()

    summary_text = ft.Text(
        f"cards {summary['cards']:,} | archetypes {summary['archetypes']:,} | "
        f"sets {summary['sets']:,} | source {summary['source']}",
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
            ft.Text(
                "Flet + DuckDB",
                size=14,
                color=ft.Colors.BLUE_GREY_600,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    keyword_input = ft.TextField(
        label="Card name / effect text",
        prefix_icon=ft.Icons.SEARCH,
        width=280,
        on_submit=lambda e: perform_search(),
    )
    type_filter = ft.Dropdown(
        label="Type",
        width=220,
        options=option_items(options["card_type"]),
    )
    attribute_filter = ft.Dropdown(
        label="Attribute",
        width=150,
        options=option_items(options["attribute"]),
    )
    race_filter = ft.Dropdown(
        label="Race",
        width=180,
        options=option_items(options["race"]),
    )
    archetype_filter = ft.Dropdown(
        label="Archetype",
        width=220,
        options=option_items(options["archetype"]),
    )
    level_filter = ft.TextField(label="Lv/Rank", width=90)
    atk_min_filter = ft.TextField(label="ATK min", width=100)
    atk_max_filter = ft.TextField(label="ATK max", width=100)
    def_min_filter = ft.TextField(label="DEF min", width=100)
    def_max_filter = ft.TextField(label="DEF max", width=100)

    result_count = ft.Text("검색 결과 0장", size=13, color=ft.Colors.GREY_700)
    result_list = ft.ListView(expand=True, spacing=6, auto_scroll=False)

    detail_title = ft.Text("카드를 선택하세요", size=18, weight="bold")
    detail_image_box = ft.Container(
        width=230,
        height=320,
        alignment=ft.Alignment.CENTER,
        border=ft.Border.all(1, ft.Colors.GREY_300),
        border_radius=6,
        content=ft.Text("No image", color=ft.Colors.GREY_600),
    )
    detail_body = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)
    detail_actions = ft.Row(spacing=4, wrap=True)
    detail_panel = ft.Container(
        width=360,
        padding=12,
        border=ft.Border.all(1, ft.Colors.GREY_300),
        border_radius=8,
        content=ft.Column(
            [
                detail_title,
                detail_image_box,
                detail_actions,
                ft.Divider(height=1),
                detail_body,
            ],
            expand=True,
            spacing=10,
        ),
    )

    deck_name = ft.TextField(label="Deck name", value="My YGO Deck", width=260)
    deck_memo = ft.TextField(label="Memo", multiline=True, min_lines=2, max_lines=3)
    ban_format = ft.Dropdown(
        label="Ban format",
        value="TCG",
        width=130,
        options=[ft.dropdown.Option(key=value, text=value) for value in BAN_FORMATS],
        on_select=lambda e: validate_current_deck(),
    )
    deck_count_text = ft.Text(size=13, color=ft.Colors.GREY_700)
    validation_text = ft.Text(size=13, color=ft.Colors.GREY_800, selectable=True)
    deck_columns = {
        section: ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, expand=True)
        for section in SECTIONS
    }

    saved_deck_list = ft.ListView(width=340, spacing=6, expand=True)
    saved_detail = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    def card_line(card):
        stats = (
            f"{fmt(card.get('attribute'))} / {fmt(card.get('race'))} / "
            f"Lv {fmt(card.get('level'))} / ATK {fmt(card.get('atk'))} / DEF {fmt(card.get('def'))}"
        )
        image_src = card.get("image_small")
        image = (
            ft.Image(src=image_src, width=46, height=64, fit=ft.BoxFit.CONTAIN)
            if image_src
            else ft.Container(width=46, height=64, bgcolor=ft.Colors.GREY_200)
        )
        return ft.Container(
            padding=8,
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=6,
            on_click=lambda e, card_id=card["id"]: select_card(card_id),
            content=ft.Row(
                [
                    image,
                    ft.Column(
                        [
                            ft.Text(card["name"], weight="bold", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(card["card_type"], size=12, color=ft.Colors.BLUE_GREY_700),
                            ft.Text(stats, size=12, color=ft.Colors.GREY_700),
                            ft.Text(fmt(card.get("archetypes")), size=12, color=ft.Colors.GREY_600),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.INFO,
                        tooltip="상세 보기",
                        on_click=lambda e, card_id=card["id"]: select_card(card_id),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        tooltip="Main Deck에 추가",
                        on_click=lambda e, card=card: add_to_deck(card, "MAIN"),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.PLAYLIST_ADD,
                        tooltip="Extra Deck에 추가",
                        on_click=lambda e, card=card: add_to_deck(card, "EXTRA"),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.AUTO_FIX_HIGH,
                        tooltip="Side Deck에 추가",
                        on_click=lambda e, card=card: add_to_deck(card, "SIDE"),
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def perform_search(e=None):
        cards = repo.search_cards(
            keyword=keyword_input.value or "",
            card_type=type_filter.value or "",
            attribute=attribute_filter.value or "",
            race=race_filter.value or "",
            archetype=archetype_filter.value or "",
            level=level_filter.value or "",
            atk_min=atk_min_filter.value or "",
            atk_max=atk_max_filter.value or "",
            def_min=def_min_filter.value or "",
            def_max=def_max_filter.value or "",
        )
        result_list.controls = [card_line(card) for card in cards]
        result_count.value = f"검색 결과 {len(cards)}장 (최대 100장 표시)"
        page.update()

    def reset_filters(e=None):
        for control in (
            keyword_input,
            level_filter,
            atk_min_filter,
            atk_max_filter,
            def_min_filter,
            def_max_filter,
        ):
            control.value = ""
        for control in (type_filter, attribute_filter, race_filter, archetype_filter):
            control.value = ""
        perform_search()

    def select_card(card_id):
        detail = repo.card_detail(int(card_id))
        if detail is None:
            show_snack("카드를 찾을 수 없습니다.", True)
            return
        selected_detail["card"] = detail
        detail_title.value = detail["name"]
        if detail.get("image_url"):
            detail_image_box.content = ft.Image(
                src=detail["image_url"],
                width=220,
                height=310,
                fit=ft.BoxFit.CONTAIN,
            )
        else:
            detail_image_box.content = ft.Text("No image", color=ft.Colors.GREY_600)

        ban_text = ", ".join(
            f"{key}: {value}" for key, value in detail["bans"].items()
        ) or "No banlist status"
        price = detail["prices"]
        set_controls = [
            ft.Text(
                f"{row['set_name']} | {fmt(row['set_code'])} | {fmt(row['rarity'])} | {fmt_price(row['set_price'])}",
                size=12,
            )
            for row in detail["sets"][:8]
        ] or [ft.Text("No set data", size=12, color=ft.Colors.GREY_600)]

        detail_body.controls = [
            ft.Text(detail["card_type"], color=ft.Colors.BLUE_GREY_700),
            ft.Text(
                f"Attribute {fmt(detail['attribute'])} | Race {fmt(detail['race'])} | "
                f"Lv/Rank {fmt(detail['level'])} | ATK {fmt(detail['atk'])} | DEF {fmt(detail['def'])}",
                size=12,
            ),
            ft.Text(f"Archetype: {fmt(detail['archetypes'])}", size=12),
            ft.Text(f"Banlist: {ban_text}", size=12, color=ft.Colors.RED_700),
            ft.Text(
                "Prices: "
                f"TCGPlayer {fmt_price(price['tcgplayer'])}, "
                f"Cardmarket {fmt_price(price['cardmarket'])}, "
                f"eBay {fmt_price(price['ebay'])}, "
                f"Amazon {fmt_price(price['amazon'])}",
                size=12,
            ),
            ft.Text(detail["description"] or "", size=12, selectable=True),
            ft.Divider(height=1),
            ft.Text("Card sets", weight="bold", size=13),
            *set_controls,
        ]
        detail_actions.controls = [
            ft.OutlinedButton(
                "Main",
                icon=ft.Icons.ADD,
                on_click=lambda e, card=detail: add_to_deck(card, "MAIN"),
            ),
            ft.OutlinedButton(
                "Extra",
                icon=ft.Icons.PLAYLIST_ADD,
                on_click=lambda e, card=detail: add_to_deck(card, "EXTRA"),
            ),
            ft.OutlinedButton(
                "Side",
                icon=ft.Icons.AUTO_FIX_HIGH,
                on_click=lambda e, card=detail: add_to_deck(card, "SIDE"),
            ),
        ]
        page.update()

    def add_to_deck(card, section):
        is_extra = bool(card.get("is_extra_deck"))
        if section == "MAIN" and is_extra:
            show_snack("Extra Deck 몬스터는 Main Deck에 넣을 수 없습니다.", True)
            return
        if section == "EXTRA" and not is_extra:
            show_snack("Extra Deck에는 Fusion/Synchro/XYZ/Link 카드만 넣을 수 있습니다.", True)
            return

        card_id = int(card["id"])
        section_cards = deck_items[section]
        if card_id not in section_cards:
            section_cards[card_id] = {
                "card_id": card_id,
                "name": card["name"],
                "card_type": card["card_type"],
                "is_extra_deck": is_extra,
                "quantity": 0,
            }
        if section_cards[card_id]["quantity"] >= 3:
            show_snack("같은 섹션에는 최대 3장까지 추가할 수 있습니다.", True)
            return
        section_cards[card_id]["quantity"] += 1
        render_deck()

    def flatten_deck():
        rows = []
        for section, cards in deck_items.items():
            for item in cards.values():
                rows.append(
                    {
                        "card_id": item["card_id"],
                        "section": section,
                        "quantity": item["quantity"],
                    }
                )
        return rows

    def change_quantity(section, card_id, delta):
        item = deck_items[section].get(card_id)
        if not item:
            return
        item["quantity"] += delta
        if item["quantity"] <= 0:
            del deck_items[section][card_id]
        elif item["quantity"] > 3:
            item["quantity"] = 3
            show_snack("카드별 최대 3장까지 가능합니다.", True)
        render_deck()

    def remove_card(section, card_id):
        deck_items[section].pop(card_id, None)
        render_deck()

    def render_deck():
        totals = {section: 0 for section in SECTIONS}
        for section in SECTIONS:
            rows = []
            for item in sorted(deck_items[section].values(), key=lambda x: x["name"]):
                totals[section] += item["quantity"]
                rows.append(
                    ft.Container(
                        padding=6,
                        border=ft.Border.all(1, ft.Colors.GREY_300),
                        border_radius=6,
                        content=ft.Row(
                            [
                                ft.Text(item["name"], expand=True, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Text(f"x{item['quantity']}", width=34, text_align=ft.TextAlign.CENTER),
                                ft.IconButton(
                                    icon=ft.Icons.REMOVE,
                                    tooltip="수량 감소",
                                    on_click=lambda e, section=section, card_id=item["card_id"]: change_quantity(section, card_id, -1),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.ADD,
                                    tooltip="수량 증가",
                                    on_click=lambda e, section=section, card_id=item["card_id"]: change_quantity(section, card_id, 1),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    tooltip="삭제",
                                    on_click=lambda e, section=section, card_id=item["card_id"]: remove_card(section, card_id),
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    )
                )
            deck_columns[section].controls = [
                ft.Text(f"{SECTION_LABELS[section]} Deck ({totals[section]})", weight="bold"),
                *rows,
            ]
        deck_count_text.value = (
            f"Main {totals['MAIN']} / Extra {totals['EXTRA']} / Side {totals['SIDE']}"
        )
        page.update()

    def validate_current_deck(e=None):
        ok, messages = repo.validate_deck(flatten_deck(), ban_format.value or "TCG")
        validation_text.value = "\n".join(messages[:10])
        validation_text.color = ft.Colors.GREEN_700 if ok else ft.Colors.RED_700
        page.update()
        return ok

    def save_current_deck(e=None):
        name = (deck_name.value or "").strip()
        if not name:
            show_snack("덱 이름을 입력하세요.", True)
            return
        try:
            deck_id = repo.save_deck(
                name=name,
                memo=deck_memo.value or "",
                ban_format=ban_format.value or "TCG",
                items=flatten_deck(),
            )
        except ValueError as exc:
            validation_text.value = str(exc)
            validation_text.color = ft.Colors.RED_700
            page.update()
            return
        refresh_saved_decks()
        show_snack(f"덱 저장 완료: #{deck_id}")

    def clear_deck(e=None):
        for section in SECTIONS:
            deck_items[section].clear()
        validation_text.value = ""
        render_deck()

    def fill_sample_deck(e=None):
        rows = repo.sample_deck_items(ban_format.value or "TCG")
        if not rows:
            show_snack("샘플 덱을 만들 카드가 부족합니다.", True)
            return
        for section in SECTIONS:
            deck_items[section].clear()
        for row in rows:
            detail = repo.card_detail(row["card_id"])
            if not detail:
                continue
            deck_items[row["section"]][row["card_id"]] = {
                "card_id": row["card_id"],
                "name": detail["name"],
                "card_type": detail["card_type"],
                "is_extra_deck": detail["is_extra_deck"],
                "quantity": row["quantity"],
            }
        render_deck()
        validate_current_deck()

    def refresh_saved_decks():
        decks = repo.list_decks()
        if not decks:
            saved_deck_list.controls = [ft.Text("저장된 덱이 없습니다.", color=ft.Colors.GREY_600)]
            saved_detail.controls = [ft.Text("덱을 저장하면 이곳에서 조회할 수 있습니다.")]
            page.update()
            return
        saved_deck_list.controls = [
            ft.Container(
                padding=8,
                border=ft.Border.all(1, ft.Colors.GREY_300),
                border_radius=6,
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(deck["name"], weight="bold"),
                                ft.Text(
                                    f"{deck['ban_format']} | {deck['total_cards']} cards | {deck['created_at']}",
                                    size=12,
                                    color=ft.Colors.GREY_700,
                                ),
                            ],
                            expand=True,
                            spacing=2,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.INFO,
                            tooltip="상세 조회",
                            on_click=lambda e, deck_id=deck["id"]: show_saved_deck(deck_id),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            tooltip="삭제",
                            on_click=lambda e, deck=deck: ask_delete_deck(deck),
                        ),
                    ]
                ),
            )
            for deck in decks
        ]
        page.update()

    def show_saved_deck(deck_id):
        detail = repo.deck_detail(int(deck_id))
        if detail is None:
            show_snack("덱을 찾을 수 없습니다.", True)
            return
        items = [
            {"card_id": row["card_id"], "section": row["section"], "quantity": row["quantity"]}
            for row in detail["cards"]
        ]
        ok, messages = repo.validate_deck(items, detail["ban_format"])
        controls = [
            ft.Text(detail["name"], size=20, weight="bold"),
            ft.Text(f"Format: {detail['ban_format']} | Created: {detail['created_at']}", size=12),
            ft.Text(detail["memo"] or "", size=12, color=ft.Colors.GREY_700),
            ft.Text(
                "\n".join(messages[:8]),
                size=12,
                color=ft.Colors.GREEN_700 if ok else ft.Colors.RED_700,
            ),
            ft.Divider(height=1),
        ]
        for section in SECTIONS:
            section_rows = [row for row in detail["cards"] if row["section"] == section]
            controls.append(ft.Text(f"{SECTION_LABELS[section]} Deck", weight="bold"))
            if not section_rows:
                controls.append(ft.Text("없음", size=12, color=ft.Colors.GREY_600))
            for row in section_rows:
                ban = f" | {row['ban_status']}" if row["ban_status"] else ""
                controls.append(
                    ft.Text(
                        f"x{row['quantity']} {row['name']} ({row['card_type']}{ban})",
                        size=12,
                    )
                )
        saved_detail.controls = controls
        page.update()

    def ask_delete_deck(deck):
        def close_dialog(e=None):
            delete_dialog.open = False
            page.update()

        def delete_now(e=None):
            repo.delete_deck(int(deck["id"]))
            close_dialog()
            refresh_saved_decks()
            show_snack(f"덱 삭제 완료: {deck['name']}")

        delete_dialog.title = ft.Text("덱 삭제")
        delete_dialog.content = ft.Text(f"'{deck['name']}' 덱을 삭제할까요?")
        delete_dialog.actions = [
            ft.TextButton("취소", on_click=close_dialog),
            ft.FilledButton("삭제", icon=ft.Icons.DELETE, on_click=delete_now),
        ]
        delete_dialog.open = True
        page.update()

    search_filters = ft.Column(
        [
            ft.Row(
                [
                    keyword_input,
                    type_filter,
                    attribute_filter,
                    race_filter,
                    archetype_filter,
                ],
                wrap=True,
                spacing=8,
            ),
            ft.Row(
                [
                    level_filter,
                    atk_min_filter,
                    atk_max_filter,
                    def_min_filter,
                    def_max_filter,
                    ft.FilledButton("Search", icon=ft.Icons.SEARCH, on_click=perform_search),
                    ft.OutlinedButton("Reset", icon=ft.Icons.CLEAR, on_click=reset_filters),
                ],
                wrap=True,
                spacing=8,
            ),
        ],
        spacing=8,
    )

    search_view = ft.Row(
        [
            ft.Container(
                expand=True,
                content=ft.Column(
                    [
                        search_filters,
                        result_count,
                        ft.Divider(height=1),
                        result_list,
                    ],
                    expand=True,
                ),
            ),
            detail_panel,
        ],
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

    deck_view = ft.Column(
        [
            ft.Row(
                [
                    deck_name,
                    ban_format,
                    ft.FilledButton("Validate", icon=ft.Icons.CHECK, on_click=validate_current_deck),
                    ft.FilledButton("Save", icon=ft.Icons.SAVE, on_click=save_current_deck),
                    ft.OutlinedButton("Sample", icon=ft.Icons.AUTO_FIX_HIGH, on_click=fill_sample_deck),
                    ft.OutlinedButton("Clear", icon=ft.Icons.CLEAR, on_click=clear_deck),
                ],
                wrap=True,
                spacing=8,
            ),
            deck_memo,
            deck_count_text,
            validation_text,
            ft.Row(
                [
                    ft.Container(
                        deck_columns["MAIN"],
                        expand=2,
                        padding=8,
                        border=ft.Border.all(1, ft.Colors.GREY_300),
                        border_radius=8,
                    ),
                    ft.Container(
                        deck_columns["EXTRA"],
                        expand=1,
                        padding=8,
                        border=ft.Border.all(1, ft.Colors.GREY_300),
                        border_radius=8,
                    ),
                    ft.Container(
                        deck_columns["SIDE"],
                        expand=1,
                        padding=8,
                        border=ft.Border.all(1, ft.Colors.GREY_300),
                        border_radius=8,
                    ),
                ],
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        ],
        expand=True,
        spacing=8,
    )

    saved_view = ft.Row(
        [
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Saved Decks", size=18, weight="bold"),
                            ft.IconButton(
                                icon=ft.Icons.REFRESH,
                                tooltip="새로고침",
                                on_click=lambda e: refresh_saved_decks(),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    saved_deck_list,
                ],
                width=360,
                expand=False,
            ),
            ft.VerticalDivider(width=1),
            saved_detail,
        ],
        expand=True,
    )

    view_host = ft.Container(content=search_view, expand=True)

    def show_view(view_name):
        if view_name == "search":
            view_host.content = search_view
        elif view_name == "deck":
            view_host.content = deck_view
        else:
            refresh_saved_decks()
            view_host.content = saved_view
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
    render_deck()
    refresh_saved_decks()
    perform_search()


if __name__ == "__main__":
    ft.run(main)
