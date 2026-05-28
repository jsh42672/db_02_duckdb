from __future__ import annotations

from typing import Any

import pandas as pd


class BaseDuckDbRepository:
    def __init__(self, connection):
        self.con = connection

    def bulk_insert(self, table: str, columns: list[str], rows: list[tuple[Any, ...]]) -> None:
        if not rows:
            return
        frame = pd.DataFrame(rows, columns=columns)
        view_name = "_bulk_rows"
        quoted_columns = ", ".join(f'"{column}"' for column in columns)
        self.con.register(view_name, frame)
        try:
            self.con.execute(
                f'INSERT INTO "{table}" ({quoted_columns}) SELECT {quoted_columns} FROM {view_name}'
            )
        finally:
            self.con.unregister(view_name)
