from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    root_dir: Path
    data_dir: Path
    db_path: Path
    cache_path: Path
    schema_path: Path
    api_url: str


def load_config(data_root: Path | None = None) -> AppConfig:
    resolved_root = Path(__file__).resolve().parent.parent
    data_dir = resolved_root / "data" if data_root is None else Path(data_root) / "data"
    return AppConfig(
        root_dir=resolved_root,
        data_dir=data_dir,
        db_path=data_dir / "ygo_cards.duckdb",
        cache_path=data_dir / "ygo_cards_cache.json",
        schema_path=resolved_root / "sql" / "schema.sql",
        api_url="https://db.ygoprodeck.com/api/v7/cardinfo.php",
    )
