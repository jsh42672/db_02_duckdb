from __future__ import annotations

import flet as ft

from domain.card.dto import CardSearchFilterDTO
from views.search.controls import SearchControls
from views.search.detail_panel import SearchDetailPanel
from views.search.result_list import SearchResultList
from views.search.state import SearchViewState


class SearchView:
    def __init__(self, page: ft.Page, search_service, detail_service, lookup_service, on_add_to_deck, show_snack):
        self.page = page
        self.search_service = search_service
        self.detail_service = detail_service
        self.lookup_service = lookup_service
        self.on_add_to_deck = on_add_to_deck
        self.show_snack = show_snack
        self.state = SearchViewState()

        # DB의 코드 테이블 값으로 필터 선택지를 구성한다.
        options = lookup_service.options()
        self.controls = SearchControls(options, self.perform_search, self.reset_filters)
        self.result_list = SearchResultList()
        self.detail_panel = SearchDetailPanel(self.on_add_to_deck)
        self.control = ft.Row(
            [
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        [
                            self.controls.control,
                            self.controls.result_count,
                            ft.Divider(height=1),
                            self.result_list.list_view,
                        ],
                        expand=True,
                    ),
                ),
                self.detail_panel.control,
            ],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

    def perform_search(self, e=None) -> None:
        # Flet 입력값을 DB와 독립적인 검색 DTO로 묶어 Service에 전달한다.
        cards = self.search_service.search(
            CardSearchFilterDTO(
                keyword=self.controls.keyword_input.value or "",
                card_type=self.controls.type_filter.value or "",
                attribute=self.controls.attribute_filter.value or "",
                race=self.controls.race_filter.value or "",
                archetype=self.controls.archetype_filter.value or "",
                level=self.controls.level_filter.value or "",
                atk_min=self.controls.atk_min_filter.value or "",
                atk_max=self.controls.atk_max_filter.value or "",
                def_min=self.controls.def_min_filter.value or "",
                def_max=self.controls.def_max_filter.value or "",
            )
        )
        self.result_list.set_cards(cards, self.select_card, self.on_add_to_deck)
        self.controls.result_count.value = f"검색 결과 {len(cards)}장 (최대 100장 표시)"
        self.page.update()

    def reset_filters(self, e=None) -> None:
        self.controls.reset()
        self.perform_search()

    def select_card(self, card_id: int) -> None:
        # 목록 DTO 대신 상세 DTO를 다시 조회해 오른쪽 패널을 갱신한다.
        detail = self.detail_service.get(int(card_id))
        if detail is None:
            self.show_snack("카드를 찾을 수 없습니다.", True)
            return
        self.state.selected_card = detail
        self.detail_panel.show_card(detail)
        self.page.update()
