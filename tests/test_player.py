from retrotune.player import PlayerState
from retrotune.sources import Track


def test_eq_filter_only_includes_active_bands():
    state = PlayerState([Track("song", "song.mp3", "Local file")])
    assert state.eq_filter() == ""
    state.adjust_gain(3)
    assert "equalizer=f=60" in state.eq_filter()


def test_playlist_navigation_wraps():
    state = PlayerState([Track("a", "a.mp3", "Local file"), Track("b", "b.mp3", "Local file")])
    assert state.current.title == "a"
    assert state.previous().title == "b"
    assert state.next().title == "a"
