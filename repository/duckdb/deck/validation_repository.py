from __future__ import annotations

from repository.duckdb.base import BaseDuckDbRepository


class DuckDbDeckValidationRepository(BaseDuckDbRepository):
    def get_validation_card_map(self, card_ids: list[int]) -> dict[int, dict[str, object]]:
        placeholders = ", ".join("?" for _ in card_ids)
        rows = self.con.execute(
            f"""
            SELECT id, name, is_extra_deck
            FROM card
            WHERE id IN ({placeholders})
            """,
            card_ids,
        ).fetchall()
        return {
            row[0]: {"name": row[1], "is_extra_deck": row[2]}
            for row in rows
        }

    def get_ban_status_map(self, card_ids: list[int], ban_format: str) -> dict[int, str]:
        placeholders = ", ".join("?" for _ in card_ids)
        rows = self.con.execute(
            f"""
            SELECT card_id, status
            FROM ban_status
            WHERE format = ?
              AND card_id IN ({placeholders})
            """,
            [ban_format, *card_ids],
        ).fetchall()
        return {row[0]: row[1] for row in rows}

    def get_legal_candidates(self, extra_deck: bool, ban_format: str, limit: int = 200) -> list[dict[str, object]]:
        rows = self.con.execute(
            """
            SELECT
                c.id,
                c.name,
                COALESCE(b.status, '') AS status
            FROM card c
            LEFT JOIN ban_status b ON b.card_id = c.id AND b.format = ?
            WHERE c.is_extra_deck = ?
            ORDER BY c.name
            LIMIT ?
            """,
            [ban_format, extra_deck, limit],
        ).fetchall()
        return [{"id": row[0], "name": row[1], "status": row[2]} for row in rows]
