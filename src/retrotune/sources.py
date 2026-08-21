from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

AUDIO_EXTENSIONS = {".aac", ".aiff", ".alac", ".flac", ".m4a", ".mp3", ".ogg", ".opus", ".wav", ".wma"}
PLAYLIST_EXTENSIONS = {".m3u", ".m3u8"}
STREAMING_HOSTS = {
    "music.youtube.com": "YouTube Music",
    "youtube.com": "YouTube",
    "youtu.be": "YouTube",
    "soundcloud.com": "SoundCloud",
    "spotify.com": "Spotify",
    "open.spotify.com": "Spotify",
}
SERVER_SCHEMES = {"plex", "navidrome", "jellyfin"}

@dataclass(frozen=True)
class Track:
    title: str
    uri: str
    source: str


def classify_source(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme in SERVER_SCHEMES:
        return parsed.scheme.capitalize()
    if parsed.scheme in {"http", "https"}:
        host = parsed.netloc.lower().removeprefix("www.")
        for needle, name in STREAMING_HOSTS.items():
            if host == needle or host.endswith("." + needle):
                return name
        return "Stream"
    path = Path(value).expanduser()
    if path.is_dir():
        return "Directory"
    if path.suffix.lower() in AUDIO_EXTENSIONS:
        return "Local file"
    if path.suffix.lower() in PLAYLIST_EXTENSIONS:
        return "Playlist"
    return "Unknown"


def expand_source(value: str) -> list[Track]:
    path = Path(value).expanduser()
    if path.is_dir():
        files = sorted(p for p in path.rglob("*") if p.suffix.lower() in AUDIO_EXTENSIONS)
        return [Track(p.stem, str(p), "Local file") for p in files]
    if path.is_file() and path.suffix.lower() in PLAYLIST_EXTENSIONS:
        return load_m3u(path)
    return [Track(path.stem or value, value, classify_source(value))]


def load_m3u(path: Path) -> list[Track]:
    tracks: list[Track] = []
    title: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#EXTINF:"):
            title = line.partition(",")[2] or None
            continue
        if line.startswith("#"):
            continue
        uri = str((path.parent / line).resolve()) if not urlparse(line).scheme and not Path(line).is_absolute() else line
        tracks.append(Track(title or Path(line).stem or line, uri, classify_source(uri)))
        title = None
    return tracks


def save_m3u(path: Path, tracks: list[Track]) -> None:
    lines = ["#EXTM3U"]
    for track in tracks:
        lines.extend([f"#EXTINF:-1,{track.title}", track.uri])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

# Backward-compatible alias for the original scaffold API.
expand_local = expand_source
