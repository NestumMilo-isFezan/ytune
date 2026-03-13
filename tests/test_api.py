import pytest
from unittest.mock import MagicMock
from ytune.api import YTuneAPI
from ytune.models import Track

def test_search_tracks_mapping(mocker):
    # Mock YTMusic class
    mock_yt = mocker.patch("ytune.api.YTMusic")
    mock_instance = mock_yt.return_value
    
    # Setup mock return value for search
    mock_instance.search.return_value = [
        {
            "videoId": "abc",
            "title": "Song Title",
            "artists": [{"name": "Artist A"}],
            "thumbnails": [{"url": "http://thumb.jpg"}]
        }
    ]
    
    api = YTuneAPI()
    results = api.search_tracks("query")
    
    assert len(results) == 1
    assert results[0].video_id == "abc"
    assert results[0].artist == "Artist A"
    assert results[0].thumbnail_url == "http://thumb.jpg"

def test_get_track_radio_mapping(mocker):
    mock_yt = mocker.patch("ytune.api.YTMusic")
    mock_instance = mock_yt.return_value
    
    mock_instance.get_watch_playlist.return_value = {
        "tracks": [
            {
                "videoId": "radio1",
                "title": "Recommended",
                "artists": [{"name": "Artist B"}],
                "thumbnails": [{"url": "thumb.jpg"}]
            }
        ]
    }
    
    api = YTuneAPI()
    results = api.get_track_radio("some_id")
    
    assert len(results) == 1
    assert results[0].video_id == "radio1"
    assert results[0].title == "Recommended"
