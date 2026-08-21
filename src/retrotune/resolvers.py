from __future__ import annotations

import json
import shutil
import subprocess

from .sources import Track, classify_source

class ResolutionError(RuntimeError):
    pass

class StreamResolver:
    """Resolve supported public streaming page URLs into player-ready URLs when tools exist."""

    def available(self) -> bool:
        return shutil.which("yt-dlp") is not None

    def resolve(self, value: str) -> Track:
        source = classify_source(value)
        if source == "Spotify":
            raise ResolutionError("Spotify links are catalog references; configure a local file/server mirror or open.spotify playback bridge.")
        if source in {"YouTube", "YouTube Music", "SoundCloud"}:
            if not self.available():
                raise ResolutionError("yt-dlp is required to resolve YouTube, YouTube Music, and SoundCloud URLs.")
            completed = subprocess.run(
                ["yt-dlp", "--dump-single-json", "--no-playlist", "--format", "bestaudio/best", value],
                check=True,
                capture_output=True,
                text=True,
            )
            metadata = json.loads(completed.stdout)
            return Track(metadata.get("title") or value, metadata.get("url") or value, source)
        return Track(value, value, source)
