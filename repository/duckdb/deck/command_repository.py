from __future__ import annotations

from domain.deck.dto import DeckItemDTO
from repository.duckdb.base import BaseDuckDbRepository


class DuckDbDeckCommandRepository(BaseDuckDbRepository):
    def save_deck(self, name: str, memo: str, ban_format: str, items: list[DeckItemDTO]) -> int:
        deck_id = self.con.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM deck").fetchone()[0]
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
        self.con.execute("DELETE FROM deck_card WHERE deck_id = ?", [deck_id])
        self.con.execute("DELETE FROM deck WHERE id = ?", [deck_id])
