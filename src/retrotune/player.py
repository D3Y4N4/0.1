from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field

from .sources import Track

@dataclass
class ParametricBand:
    frequency_hz: int
    gain_db: float = 0.0
    q: float = 1.0

    def ffmpeg_filter(self) -> str:
        return f"equalizer=f={self.frequency_hz}:width_type=q:width={self.q}:g={self.gain_db}"

@dataclass
class PlayerState:
    playlist: list[Track] = field(default_factory=list)
    current_index: int = 0
    playing: bool = False
    selected_band: int = 0
    eq: list[ParametricBand] = field(default_factory=lambda: [
        ParametricBand(60), ParametricBand(170), ParametricBand(310), ParametricBand(600),
        ParametricBand(1000), ParametricBand(3000), ParametricBand(6000), ParametricBand(12000),
    ])

    @property
    def current(self) -> Track | None:
        if not self.playlist:
            return None
        return self.playlist[self.current_index % len(self.playlist)]

    def next(self) -> Track | None:
        if self.playlist:
            self.current_index = (self.current_index + 1) % len(self.playlist)
        return self.current

    def previous(self) -> Track | None:
        if self.playlist:
            self.current_index = (self.current_index - 1) % len(self.playlist)
        return self.current

    def adjust_gain(self, amount: float) -> None:
        band = self.eq[self.selected_band]
        band.gain_db = max(-12.0, min(12.0, band.gain_db + amount))

    def eq_filter(self) -> str:
        active = [band.ffmpeg_filter() for band in self.eq if band.gain_db]
        return ",".join(active)

class MpvBackend:
    """mpv wrapper with IPC-friendly flags for local files and resolved network streams."""

    def __init__(self) -> None:
        self.proc: subprocess.Popen[str] | None = None

    def available(self) -> bool:
        return shutil.which("mpv") is not None

    def command_for(self, track: Track, state: PlayerState) -> list[str]:
        command = ["mpv", "--no-video", "--really-quiet"]
        filters = state.eq_filter()
        if filters:
            command.append(f"--af={filters}")
        command.append(track.uri)
        return command

    def play(self, track: Track, state: PlayerState) -> None:
        self.stop()
        self.proc = subprocess.Popen(self.command_for(track, state), text=True)
        state.playing = True

    def stop(self) -> None:
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
        self.proc = None
