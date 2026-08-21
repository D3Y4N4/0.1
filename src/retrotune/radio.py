from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.parse import urlencode
from urllib.request import urlopen

@dataclass(frozen=True)
class RadioStation:
    name: str
    url: str
    country: str = ""
    tags: str = ""

class RadioBrowser:
    """Client for the community Radio Browser directory of thousands of stations."""

    base_url = "https://de1.api.radio-browser.info/json/stations/search"

    def search(self, query: str, *, limit: int = 25) -> list[RadioStation]:
        params = urlencode({"name": query, "limit": limit, "hidebroken": "true", "order": "clickcount", "reverse": "true"})
        with urlopen(f"{self.base_url}?{params}", timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return [
            RadioStation(item.get("name", "Untitled"), item.get("url_resolved") or item.get("url", ""), item.get("country", ""), item.get("tags", ""))
            for item in payload if item.get("url_resolved") or item.get("url")
        ]
