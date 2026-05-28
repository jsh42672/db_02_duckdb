from __future__ import annotations

from repository.duckdb.base import BaseDuckDbRepository


class DuckDbSeedMetaRepository(BaseDuckDbRepository):
    def get_meta_value(self, key: str) -> str | None:
        row = self.con.execute("SELECT value FROM seed_meta WHERE key = ?", [key]).fetchone()
        return row[0] if row else None

    def set_meta_value(self, key: str, value: str) -> None:
        self.con.execute("DELETE FROM seed_meta WHERE key = ?", [key])
        self.con.execute("INSERT INTO seed_meta VALUES (?, ?)", [key, value])
