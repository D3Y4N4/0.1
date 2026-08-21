# RetroTune

RetroTune is a standalone command-line music player for macOS and Linux with a retro terminal interface inspired by classic Winamp.

## Features

- Local playback queue support for individual audio files, M3U/M3U8 playlists, and recursively scanned directories.
- Streaming source recognition for YouTube, YouTube Music, SoundCloud, Spotify, and arbitrary HTTP streams.
- Optional `yt-dlp` resolution for YouTube, YouTube Music, and SoundCloud URLs before they are handed to the player.
- Personal media server search hooks for Plex, Navidrome/Subsonic, and Jellyfin via environment-configured server URLs and tokens.
- Curses-based terminal UI with a spectrum visualizer, track navigation, and an in-terminal parametric EQ panel.
- Playlist-oriented player state with M3U export for queues assembled from files, folders, streams, radio stations, and server searches.
- Online radio search through the community Radio Browser directory of thousands of stations.
- `mpv` backend integration for reliable cross-platform audio playback on Mac and Linux, including generated FFmpeg equalizer filters.

## Install

```bash
python -m pip install -e .
```

For best playback support, install `mpv`. For streaming services that require URL extraction, install the optional streaming tools:

```bash
python -m pip install -e '.[streaming]'
```

## Usage

Launch the retro UI with local files, folders, playlists, or stream URLs:

```bash
retrotune ~/Music favorites.m3u https://youtube.com/watch?v=dQw4w9WgXcQ
```

Preview the resolved playlist without opening curses:

```bash
retrotune --no-ui ~/Music
```

Resolve public streaming pages with `yt-dlp` before playback:

```bash
retrotune --resolve 'https://music.youtube.com/watch?v=dQw4w9WgXcQ'
```

Export a queue to an M3U playlist:

```bash
retrotune --no-ui --save-playlist queue.m3u ~/Music https://soundcloud.com/example/song
```

Search online radio stations:

```bash
retrotune --radio jazz
```

Search a personal media server:

```bash
RETROTUNE_JELLYFIN_URL=http://localhost:8096 \
RETROTUNE_JELLYFIN_TOKEN=your-token \
retrotune --server jellyfin --search "Herbie Hancock"
```

Supported server environment variables are `RETROTUNE_PLEX_URL` / `RETROTUNE_PLEX_TOKEN`, `RETROTUNE_NAVIDROME_URL` / `RETROTUNE_NAVIDROME_TOKEN`, and `RETROTUNE_JELLYFIN_URL` / `RETROTUNE_JELLYFIN_TOKEN`. Navidrome also honors `RETROTUNE_NAVIDROME_USER` and treats `RETROTUNE_NAVIDROME_TOKEN` as the Subsonic password used to generate salted token authentication; Plex and Jellyfin use their native API tokens.

## Terminal controls

- `q` or `Esc`: quit
- `n` / `p`: next or previous track
- `←` / `→`: choose an EQ band
- `+` / `-`: raise or lower the selected EQ band
- `Space`: restart playback with the current EQ settings
