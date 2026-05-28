from __future__ import annotations

import json
import urllib.request


class YgoProDeckClient:
    def __init__(self, api_url: str):
        self.api_url = api_url

    def fetch_payload(self) -> dict:
        request = urllib.request.Request(
            self.api_url,
            headers={"User-Agent": "db-term-project-ygo/1.0"},
        )
        with urllib.request.urlopen(request, timeout=45) as response:
            return json.loads(response.read().decode("utf-8"))
