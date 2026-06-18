from __future__ import annotations

from pathlib import Path

from repository.duckdb.base import BaseDuckDbRepository


class DuckDbSeedSchemaRepository(BaseDuckDbRepository):
    def __init__(self, connection, schema_path: Path):
        super().__init__(connection)
        self.schema_path = schema_path

    def apply_schema(self) -> None:
        self._prepare_legacy_tables_for_schema()
        self.con.execute(self.schema_path.read_text(encoding="utf-8"))
        self._migrate_legacy_bcnf_tables()

    def _columns(self, table_name: str) -> set[str]:
        rows = self.con.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'main'
              AND table_name = ?
            """,
            [table_name],
        ).fetchall()
        return {row[0] for row in rows}

    def _table_exists(self, table_name: str) -> bool:
        row = self.con.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'main'
              AND table_name = ?
            """,
            [table_name],
        ).fetchone()
        return bool(row and row[0])

    def _prepare_legacy_tables_for_schema(self) -> None:
        if self._table_exists("card_set") and "release_year" not in self._columns("card_set"):
            self.con.execute("ALTER TABLE card_set ADD COLUMN release_year SMALLINT")

    def _migrate_legacy_bcnf_tables(self) -> None:
        has_legacy_price = self._table_exists("card_price") and "cardmarket" in self._columns("card_price")
        has_legacy_rarity = self._table_exists("card_set_entry") and "rarity_code" in self._columns("card_set_entry")
        if has_legacy_price:
            self._migrate_card_price()
        if has_legacy_rarity:
            self._migrate_card_set_entry()
        if self._table_exists("card_set"):
            self._ensure_card_set_release_year()
        if self._table_exists("ban_status"):
            self._backfill_ban_code_tables()
        if self._table_exists("deck") and self._table_exists("deck_card"):
            self._backfill_deck_section_table()

    def _ensure_card_set_release_year(self) -> None:
        if "release_year" not in self._columns("card_set"):
            self.con.execute("ALTER TABLE card_set ADD COLUMN release_year SMALLINT")

    def _migrate_card_price(self) -> None:
        self.con.execute("ALTER TABLE card_price RENAME TO card_price_legacy")
        self.con.execute(
            """
            CREATE TABLE card_price (
                card_id BIGINT NOT NULL REFERENCES card(id),
                source_name VARCHAR NOT NULL REFERENCES price_source(name),
                price DECIMAL(10, 2),
                PRIMARY KEY (card_id, source_name)
            )
            """
        )
        for source_name in ("cardmarket", "tcgplayer", "ebay", "amazon", "coolstuffinc"):
            self.con.execute(
                f"""
                INSERT OR IGNORE INTO card_price (card_id, source_name, price)
                SELECT card_id, ?, {source_name}
                FROM card_price_legacy
                WHERE {source_name} IS NOT NULL
                """,
                [source_name],
            )
        self.con.execute("DROP TABLE card_price_legacy")

    def _migrate_card_set_entry(self) -> None:
        self.con.execute(
            """
            INSERT OR IGNORE INTO rarity (name, code)
            SELECT DISTINCT rarity, rarity_code
            FROM card_set_entry
            WHERE rarity IS NOT NULL
            """
        )
        self.con.execute("ALTER TABLE card_set_entry RENAME TO card_set_entry_legacy")
        self.con.execute(
            """
            CREATE TABLE card_set_entry (
                id BIGINT PRIMARY KEY,
                card_id BIGINT NOT NULL REFERENCES card(id),
                set_name VARCHAR NOT NULL REFERENCES card_set(name),
                set_code VARCHAR,
                rarity VARCHAR REFERENCES rarity(name),
                set_price DECIMAL(10, 2),
                UNIQUE (card_id, set_code, rarity)
            )
            """
        )
        self.con.execute(
            """
            INSERT OR IGNORE INTO card_set_entry
                (id, card_id, set_name, set_code, rarity, set_price)
            SELECT id, card_id, set_name, set_code, rarity, set_price
            FROM card_set_entry_legacy
            """
        )
        self.con.execute("DROP TABLE card_set_entry_legacy")

    def _backfill_ban_code_tables(self) -> None:
        self.con.execute(
            """
            INSERT OR IGNORE INTO ban_format (name)
            SELECT DISTINCT format
            FROM ban_status
            WHERE format IS NOT NULL
            """
        )
        self.con.execute(
            """
            INSERT OR IGNORE INTO ban_status_type (name)
            SELECT DISTINCT status
            FROM ban_status
            WHERE status IS NOT NULL
            """
        )

    def _backfill_deck_section_table(self) -> None:
        self.con.execute(
            """
            INSERT OR IGNORE INTO ban_format (name)
            SELECT DISTINCT ban_format
            FROM deck
            WHERE ban_format IS NOT NULL
            """
        )
        self.con.execute(
            """
            INSERT OR IGNORE INTO deck_section (name)
            SELECT DISTINCT section
            FROM deck_card
            WHERE section IS NOT NULL
            """
        )

    def replace_catalog(self) -> None:
        for table in (
            "deck_card_role",
            "deck_card",
            "deck",
            "card_image",
            "card_price",
            "ban_status",
            "card_set_entry",
            "card_archetype",
            "card",
            "card_release",
            "card_set_release",
            "card_set",
            "role_tag",
            "price_source",
            "deck_section",
            "ban_status_type",
            "ban_format",
            "rarity",
            "archetype",
            "race",
            "attribute",
            "card_type",
            "seed_meta",
        ):
            self.con.execute(f"DROP TABLE IF EXISTS {table}")
        self.apply_schema()
