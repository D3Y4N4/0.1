from retrotune.servers import ServerConfig, parse_jellyfin_tracks, parse_navidrome_tracks, parse_plex_tracks


def test_parse_plex_tracks_returns_stream_urls():
    payload = '<MediaContainer><Hub><Track title="Song" key="/library/parts/1/file.mp3" /></Hub></MediaContainer>'
    tracks = parse_plex_tracks(payload, ServerConfig("http://plex", "secret"))
    assert tracks[0].title == "Song"
    assert tracks[0].uri == "http://plex/library/parts/1/file.mp3?X-Plex-Token=secret"


def test_parse_jellyfin_tracks_returns_audio_streams():
    tracks = parse_jellyfin_tracks({"Items": [{"Name": "Song", "Id": "abc"}]}, ServerConfig("http://jellyfin", "secret"))
    assert tracks[0].uri == "http://jellyfin/Audio/abc/stream?api_key=secret"


def test_parse_navidrome_tracks_uses_supplied_auth_params():
    payload = {"subsonic-response": {"searchResult3": {"song": [{"title": "Song", "id": "42"}]}}}
    tracks = parse_navidrome_tracks(payload, ServerConfig("http://navidrome", "secret", "me"), {"u": "me", "t": "digest", "s": "salt"})
    assert tracks[0].uri == "http://navidrome/rest/stream.view?id=42&v=1.16.1&c=retrotune&u=me&t=digest&s=salt"
