from __future__ import annotations

import json
import urllib.error
from pathlib import Path

from app.config import AppConfig
from domain.seed.dto import SeedCardDTO
from provider.interfaces import CardDataProvider
from provider.ygoprodeck.cache import read_card_cache, write_card_cache
from provider.ygoprodeck.client import YgoProDeckClient
from provider.ygoprodeck.fallback import fallback_cards
from provider.ygoprodeck.mapper import map_api_cards


class YgoProDeckProvider(CardDataProvider):
    def __init__(self, config: AppConfig):
        self.config = config
        self.client = YgoProDeckClient(config.api_url)

    def fetch_cards(self) -> tuple[list[SeedCardDTO], str]:
        cached_payload = read_card_cache(self.config.cache_path)
        if cached_payload is not None:
            return map_api_cards(cached_payload.get("data", cached_payload)), "cache"

        try:
            payload = self.client.fetch_payload()
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            return fallback_cards(), "fallback"

        write_card_cache(self.config.cache_path, payload)
        return map_api_cards(payload.get("data", payload)), "api"
