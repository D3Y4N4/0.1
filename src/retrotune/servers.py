from __future__ import annotations

import hashlib
import json
import os
import secrets
from dataclasses import dataclass
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from .sources import Track

@dataclass(frozen=True)
class ServerConfig:
    base_url: str
    token: str
    username: str = "retrotune"

class MediaServerClient:
    """Search clients that return playable stream URLs for Plex, Navidrome/Subsonic, and Jellyfin."""

    def _config(self, name: str) -> ServerConfig:
        prefix = name.upper()
        base_url = os.environ.get(f"RETROTUNE_{prefix}_URL", "").rstrip("/")
        token = os.environ.get(f"RETROTUNE_{prefix}_TOKEN", "")
        username = os.environ.get(f"RETROTUNE_{prefix}_USER", "retrotune")
        if not base_url or not token:
            raise RuntimeError(f"Set RETROTUNE_{prefix}_URL and RETROTUNE_{prefix}_TOKEN to browse {name}.")
        return ServerConfig(base_url, token, username)

    def search(self, server: str, query: str, *, limit: int = 25) -> list[Track]:
        server = server.lower()
        if server == "plex":
            return self._plex(query, limit)
        if server == "jellyfin":
            return self._jellyfin(query, limit)
        if server == "navidrome":
            return self._navidrome(query, limit)
        raise ValueError(f"Unsupported server: {server}")

    def _plex(self, query: str, limit: int) -> list[Track]:
        cfg = self._config("plex")
        url = f"{cfg.base_url}/hubs/search?{urlencode({'query': query, 'limit': limit, 'X-Plex-Token': cfg.token})}"
        with urlopen(url, timeout=10) as response:
            payload = response.read().decode("utf-8", "ignore")
        return parse_plex_tracks(payload, cfg)

    def _jellyfin(self, query: str, limit: int) -> list[Track]:
        cfg = self._config("jellyfin")
        url = f"{cfg.base_url}/Items?{urlencode({'searchTerm': query, 'includeItemTypes': 'Audio', 'recursive': 'true', 'limit': limit})}"
        request = Request(url, headers={"X-Emby-Token": cfg.token})
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return parse_jellyfin_tracks(payload, cfg)

    def _navidrome(self, query: str, limit: int) -> list[Track]:
        cfg = self._config("navidrome")
        auth = subsonic_auth_params(cfg)
        params = {"query": query, "songCount": limit, "f": "json", "v": "1.16.1", "c": "retrotune", **auth}
        url = f"{cfg.base_url}/rest/search3.view?{urlencode(params)}"
        with urlopen(url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return parse_navidrome_tracks(payload, cfg, auth)


def parse_plex_tracks(payload: str, cfg: ServerConfig) -> list[Track]:
    root = ElementTree.fromstring(payload)
    tracks: list[Track] = []
    for element in root.iter():
        if element.tag.rsplit('}', 1)[-1] != "Track":
            continue
        key = element.attrib.get("key")
        title = element.attrib.get("title") or element.attrib.get("grandparentTitle") or "Plex track"
        if key:
            tracks.append(Track(title, f"{cfg.base_url}{key}?X-Plex-Token={quote(cfg.token)}", "Plex"))
    return tracks


def parse_jellyfin_tracks(payload: dict, cfg: ServerConfig) -> list[Track]:
    return [
        Track(item.get("Name", "Jellyfin track"), f"{cfg.base_url}/Audio/{item['Id']}/stream?api_key={quote(cfg.token)}", "Jellyfin")
        for item in payload.get("Items", [])
        if item.get("Id")
    ]


def parse_navidrome_tracks(payload: dict, cfg: ServerConfig, auth: dict[str, str]) -> list[Track]:
    songs = payload.get("subsonic-response", {}).get("searchResult3", {}).get("song", [])
    auth_query = urlencode({"v": "1.16.1", "c": "retrotune", **auth})
    return [
        Track(song.get("title", "Navidrome track"), f"{cfg.base_url}/rest/stream.view?id={quote(str(song['id']))}&{auth_query}", "Navidrome")
        for song in songs
        if song.get("id")
    ]


def subsonic_auth_params(cfg: ServerConfig) -> dict[str, str]:
    salt = secrets.token_hex(6)
    digest = hashlib.md5(f"{cfg.token}{salt}".encode("utf-8")).hexdigest()
    return {"u": cfg.username, "t": digest, "s": salt}


def parse_server_uri(uri: str) -> tuple[str, str]:
    parsed = urlparse(uri)
    return parsed.scheme, (parsed.netloc + parsed.path).strip("/")
