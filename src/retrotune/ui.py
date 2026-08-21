from __future__ import annotations

import curses
import math
import random
import time

from .player import MpvBackend, PlayerState

LOGO = "RETROTUNE // terminal Winamp vibes"

class RetroUI:
    def __init__(self, state: PlayerState, backend: MpvBackend | None = None) -> None:
        self.state = state
        self.backend = backend
        self.rng = random.Random(7)

    def run(self) -> None:
        curses.wrapper(self._draw_loop)

    def _draw_loop(self, screen: curses.window) -> None:
        curses.curs_set(0)
        screen.nodelay(True)
        while True:
            ch = screen.getch()
            if ch in {ord("q"), 27}:
                break
            self._handle_key(ch)
            self._render(screen)
            time.sleep(0.08)

    def _handle_key(self, ch: int) -> None:
        if ch == ord("+"):
            self.state.adjust_gain(1.0)
        elif ch == ord("-"):
            self.state.adjust_gain(-1.0)
        elif ch == curses.KEY_RIGHT:
            self.state.selected_band = min(len(self.state.eq) - 1, self.state.selected_band + 1)
        elif ch == curses.KEY_LEFT:
            self.state.selected_band = max(0, self.state.selected_band - 1)
        elif ch == ord("n"):
            self.state.next()
            self._restart()
        elif ch == ord("p"):
            self.state.previous()
            self._restart()
        elif ch == ord(" "):
            self._restart()

    def _restart(self) -> None:
        if self.backend and self.state.current and self.backend.available():
            self.backend.play(self.state.current, self.state)

    def _render(self, screen: curses.window) -> None:
        screen.erase()
        height, width = screen.getmaxyx()
        track = self.state.current
        screen.addstr(0, 0, LOGO[: width - 1], curses.A_BOLD)
        screen.addstr(1, 0, f"Now: {track.title if track else 'nothing queued'}"[: width - 1])
        self._visualizer(screen, 3, 0, max(4, height // 3), width)
        self._eq(screen, max(8, height // 2), 0, max(5, height // 3), width)
        screen.addstr(height - 2, 0, "Keys: q quit | n/p track | ←/→ EQ band | +/- gain | space restart"[: width - 1])
        screen.refresh()

    def _visualizer(self, screen: curses.window, y: int, x: int, h: int, w: int) -> None:
        bars = max(8, min(64, w // 2))
        phase = time.time() * 4
        for i in range(bars):
            level = int((math.sin(phase + i * 0.45) + 1.2 + self.rng.random() * 0.8) / 3 * h)
            for row in range(level):
                screen.addstr(y + h - row, x + i * 2, "█")

    def _eq(self, screen: curses.window, y: int, x: int, h: int, w: int) -> None:
        screen.addstr(y, x, "Parametric EQ: frequency / gain / Q"[: w - 1], curses.A_BOLD)
        for idx, band in enumerate(self.state.eq[: max(1, (w - 2) // 12)]):
            col = x + idx * 12
            zero = y + h // 2
            gain_rows = round(band.gain_db / 3)
            label = f"{band.frequency_hz:g}Hz"
            attr = curses.A_REVERSE if idx == self.state.selected_band else curses.A_NORMAL
            screen.addstr(y + h - 1, col, label[:10], attr)
            screen.addstr(zero, col, "─")
            marker_y = max(y + 1, min(y + h - 2, zero - gain_rows))
            screen.addstr(marker_y, col, "◆", attr)
