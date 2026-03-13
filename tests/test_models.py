import pytest
from ytune.models import Track, Album, Playlist

def test_track_model_alias():
    raw_data = {
        "videoId": "aqz-KE-bpKQ",
        "title": "Never Gonna Give You Up",
        "artists": [{"name": "Rick Astley"}],
        "artist": "Rick Astley",
        "album": "Whenever You Need Somebody",
        "duration": "3:33",
        "thumbnails": [{"url": "http://example.com/img.jpg"}]
    }
    # Test that videoId is correctly aliased to video_id
    track = Track.model_validate(raw_data)
    assert track.video_id == "aqz-KE-bpKQ"
    assert track.title == "Never Gonna Give You Up"
    assert track.artist == "Rick Astley"

def test_track_model_optional_fields():
    raw_data = {
        "videoId": "123",
        "title": "Test Title",
        "artist": "Test Artist"
    }
    track = Track.model_validate(raw_data)
    assert track.album is None
    assert track.duration is None
    assert track.thumbnail_url is None

def test_album_model_alias():
    raw_data = {
        "browseId": "alb123",
        "title": "Test Album",
        "artist": "Test Artist",
        "year": "2024"
    }
    album = Album.model_validate(raw_data)
    assert album.album_id == "alb123"
    assert album.year == "2024"

def test_playlist_model_alias():
    raw_data = {
        "playlistId": "pl123",
        "title": "Test Playlist",
        "count": 10
    }
    playlist = Playlist.model_validate(raw_data)
    assert playlist.playlist_id == "pl123"
    assert playlist.count == 10
