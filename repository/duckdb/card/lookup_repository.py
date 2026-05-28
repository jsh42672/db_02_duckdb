from __future__ import annotations

from domain.card.dto import AppSummaryDTO, LookupOptionsDTO
from repository.duckdb.base import BaseDuckDbRepository


class DuckDbLookupRepository(BaseDuckDbRepository):
    def _names(self, table: str) -> list[str]:
        rows = self.con.execute(f"SELECT name FROM {table} ORDER BY name").fetchall()
        return [row[0] for row in rows]

    def get_lookup_options(self) -> LookupOptionsDTO:
        return LookupOptionsDTO(
            card_type=self._names("card_type"),
            attribute=self._names("attribute"),
            race=self._names("race"),
            archetype=self._names("archetype"),
        )

    def get_summary(self) -> AppSummaryDTO:
        row = self.con.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM card) AS cards,
                (SELECT COUNT(*) FROM archetype) AS archetypes,
                (SELECT COUNT(*) FROM card_set) AS sets,
                (SELECT COUNT(*) FROM deck) AS decks
            """
        ).fetchone()
        meta = {
            key: value
            for key, value in self.con.execute("SELECT key, value FROM seed_meta").fetchall()
        }
        return AppSummaryDTO(
            cards=row[0],
            archetypes=row[1],
            sets=row[2],
            decks=row[3],
            source=meta.get("seed_source", "unknown"),
        )
