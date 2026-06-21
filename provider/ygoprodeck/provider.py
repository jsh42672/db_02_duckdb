from __future__ import annotations

import json
import urllib.error
from pathlib import Path

from app.config import AppConfig
from domain.seed.dto import SeedCardDTO
from provider.interfaces import ICardDataProvider
from provider.ygoprodeck.cache import read_card_cache, write_card_cache
from provider.ygoprodeck.client import YgoProDeckClient
from provider.ygoprodeck.fallback import fallback_cards
from provider.ygoprodeck.mapper import map_api_cards


class YgoProDeckProvider(ICardDataProvider):
    def __init__(self, config: AppConfig):
        self.config = config
        self.client = YgoProDeckClient(config.api_url)

    def fetch_cards(self) -> tuple[list[SeedCardDTO], str]:
        # 반복 실행 시 API 호출을 줄이기 위해 유효한 로컬 캐시를 가장 먼저 사용한다.
        cached_payload = read_card_cache(self.config.cache_path)
        if cached_payload is not None:
            return map_api_cards(cached_payload.get("data", cached_payload)), "cache"

        try:
            payload = self.client.fetch_payload()
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            # 네트워크나 JSON 문제가 있어도 앱을 실행할 수 있도록 최소 카드 데이터를 반환한다.
            return fallback_cards(), "fallback"

        # 정상 응답은 다음 실행에서 재사용할 수 있도록 원본 JSON 형태로 보관한다.
        write_card_cache(self.config.cache_path, payload)
        return map_api_cards(payload.get("data", payload)), "api"
