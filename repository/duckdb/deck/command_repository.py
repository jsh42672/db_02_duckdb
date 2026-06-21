from __future__ import annotations

from domain.deck.dto import DeckItemDTO
from repository.duckdb.base import BaseDuckDbRepository


class DuckDbDeckCommandRepository(BaseDuckDbRepository):
    def save_deck(self, name: str, memo: str, ban_format: str, items: list[DeckItemDTO]) -> int:
        # DuckDB 단일 파일 환경에서 사용할 새 덱 ID를 생성한다.
        deck_id = self.con.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM deck").fetchone()[0]
        # deck과 deck_card는 하나의 단위이므로 둘 중 하나라도 실패하면 전체를 되돌린다.
        self.con.execute("BEGIN TRANSACTION")
        try:
            self.con.execute(
                "INSERT INTO deck (id, name, memo, ban_format) VALUES (?, ?, ?, ?)",
                [deck_id, name, memo, ban_format],
            )
            rows = [
                (deck_id, int(item.card_id), item.section, int(item.quantity))
                for item in items
            ]
            self.con.executemany("INSERT INTO deck_card VALUES (?, ?, ?, ?)", rows)
            self.con.execute("COMMIT")
        except Exception:
            self.con.execute("ROLLBACK")
            raise
        return int(deck_id)

    def delete_deck(self, deck_id: int) -> None:
        # 외래키 관계를 고려해 자식 행을 먼저 제거한다.
        self.con.execute("DELETE FROM deck_card WHERE deck_id = ?", [deck_id])
        self.con.execute("DELETE FROM deck WHERE id = ?", [deck_id])
