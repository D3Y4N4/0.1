from __future__ import annotations

import argparse
from pathlib import Path

from .player import MpvBackend, PlayerState
from .radio import RadioBrowser
from .resolvers import ResolutionError, StreamResolver
from .servers import MediaServerClient
from .sources import Track, expand_source, save_m3u
from .ui import RetroUI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RetroTune: a Winamp-inspired terminal music player")
    parser.add_argument("sources", nargs="*", help="Files, directories, playlists, stream URLs, or plex:/navidrome:/jellyfin: URIs")
    parser.add_argument("--radio", metavar="QUERY", help="Search online radio stations and print playable URLs")
    parser.add_argument("--server", choices=["plex", "navidrome", "jellyfin"], help="Search a configured personal media server")
    parser.add_argument("--search", metavar="QUERY", help="Search text for --server")
    parser.add_argument("--resolve", action="store_true", help="Resolve YouTube/YouTube Music/SoundCloud URLs with yt-dlp before playback")
    parser.add_argument("--save-playlist", metavar="PATH", help="Write the resolved queue as an M3U playlist")
    parser.add_argument("--no-ui", action="store_true", help="Resolve playlist without launching the terminal UI")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.radio:
        for station in RadioBrowser().search(args.radio):
            print(f"{station.name}\t{station.country}\t{station.url}")
        return 0
    if args.server:
        if not args.search:
            raise SystemExit("--server requires --search")
        for track in MediaServerClient().search(args.server, args.search):
            print(f"{track.source}: {track.title} -> {track.uri}")
        return 0

    playlist = build_playlist(args.sources, resolve=args.resolve)
    if args.save_playlist:
        save_m3u(Path(args.save_playlist), playlist)
    state = PlayerState(playlist=playlist)
    if args.no_ui:
        for track in state.playlist:
            print(f"{track.source}: {track.title} -> {track.uri}")
        return 0
    backend = MpvBackend()
    if state.current and backend.available():
        backend.play(state.current, state)
    try:
        RetroUI(state, backend).run()
    finally:
        backend.stop()
    return 0


def build_playlist(sources: list[str], *, resolve: bool = False) -> list[Track]:
    resolver = StreamResolver()
    playlist: list[Track] = []
    for source in sources:
        expanded = expand_source(source)
        if resolve:
            for track in expanded:
                try:
                    playlist.append(resolver.resolve(track.uri))
                except ResolutionError as exc:
                    raise SystemExit(str(exc)) from exc
        else:
            playlist.extend(expanded)
    return playlist

if __name__ == "__main__":
    raise SystemExit(main())
