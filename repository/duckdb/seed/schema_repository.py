from __future__ import annotations

from pathlib import Path

from repository.duckdb.base import BaseDuckDbRepository


class DuckDbSeedSchemaRepository(BaseDuckDbRepository):
    def __init__(self, connection, schema_path: Path):
        super().__init__(connection)
        self.schema_path = schema_path

    def apply_schema(self) -> None:
        self.con.execute(self.schema_path.read_text(encoding="utf-8"))

    def replace_catalog(self) -> None:
        for table in (
            "deck_card",
            "deck",
            "card_image",
            "card_price",
            "ban_status",
            "card_set_entry",
            "card_archetype",
            "card",
            "card_set",
            "archetype",
            "race",
            "attribute",
            "card_type",
            "seed_meta",
        ):
            self.con.execute(f"DROP TABLE IF EXISTS {table}")
        self.apply_schema()
