from pathlib import Path

from retrotune.sources import classify_source, expand_source, load_m3u, save_m3u


def test_classifies_streaming_services():
    assert classify_source("https://youtube.com/watch?v=x") == "YouTube"
    assert classify_source("https://music.youtube.com/watch?v=x") == "YouTube Music"
    assert classify_source("https://soundcloud.com/a/b") == "SoundCloud"
    assert classify_source("https://open.spotify.com/track/1") == "Spotify"


def test_classifies_personal_media_servers():
    assert classify_source("plex://library/track/1") == "Plex"
    assert classify_source("navidrome://album/2") == "Navidrome"
    assert classify_source("jellyfin://items/3") == "Jellyfin"


def test_expands_directory(tmp_path):
    (tmp_path / "song.mp3").write_text("fake")
    (tmp_path / "notes.txt").write_text("skip")
    tracks = expand_source(str(tmp_path))
    assert [track.title for track in tracks] == ["song"]


def test_m3u_round_trip(tmp_path):
    playlist = tmp_path / "mix.m3u"
    source = tmp_path / "song.flac"
    source.write_text("fake")
    save_m3u(playlist, expand_source(str(source)))
    tracks = load_m3u(playlist)
    assert tracks[0].title == "song"
    assert Path(tracks[0].uri) == source
