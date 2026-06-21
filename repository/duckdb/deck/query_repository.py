from __future__ import annotations

from domain.deck.dto import SavedDeckCardDTO, SavedDeckDetailDTO, SavedDeckSummaryDTO
from repository.duckdb.base import BaseDuckDbRepository


class DuckDbDeckQueryRepository(BaseDuckDbRepository):
    def deck_count(self) -> int:
        return self.con.execute("SELECT COUNT(*) FROM deck").fetchone()[0]

    def list_decks(self) -> list[SavedDeckSummaryDTO]:
        # 목록 화면은 덱 기본 정보와 전체 카드 수만 집계해 가볍게 조회한다.
        rows = self.con.execute(
            """
            SELECT
                d.id,
                d.name,
                d.ban_format,
                d.created_at,
                COALESCE(SUM(dc.quantity), 0) AS total_cards
            FROM deck d
            LEFT JOIN deck_card dc ON dc.deck_id = d.id
            GROUP BY d.id, d.name, d.ban_format, d.created_at
            ORDER BY d.created_at DESC
            """
        ).fetchall()
        return [
            SavedDeckSummaryDTO(
                id=row[0],
                name=row[1],
                ban_format=row[2],
                created_at=row[3],
                total_cards=row[4],
            )
            for row in rows
        ]

    def get_deck_detail(self, deck_id: int) -> SavedDeckDetailDTO | None:
        deck = self.con.execute(
            "SELECT id, name, memo, ban_format, created_at FROM deck WHERE id = ?",
            [deck_id],
        ).fetchone()
        if deck is None:
            return None

        # 상세 화면에서는 카드 정보와 해당 덱 포맷의 금지 제한 상태를 함께 Join한다.
        rows = self.con.execute(
            """
            SELECT
                dc.section,
                dc.quantity,
                c.id,
                c.name,
                c.card_type,
                c.is_extra_deck,
                b.status
            FROM deck_card dc
            JOIN card c ON c.id = dc.card_id
            JOIN deck d ON d.id = dc.deck_id
            LEFT JOIN ban_status b ON b.card_id = c.id AND b.format = d.ban_format
            WHERE dc.deck_id = ?
            ORDER BY dc.section, c.name
            """,
            [deck_id],
        ).fetchall()
        return SavedDeckDetailDTO(
            id=deck[0],
            name=deck[1],
            memo=deck[2],
            ban_format=deck[3],
            created_at=deck[4],
            cards=[
                SavedDeckCardDTO(
                    section=row[0],
                    quantity=row[1],
                    card_id=row[2],
                    name=row[3],
                    card_type=row[4],
                    is_extra_deck=row[5],
                    ban_status=row[6],
                )
                for row in rows
            ],
        )
