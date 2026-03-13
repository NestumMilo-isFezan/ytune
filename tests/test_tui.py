import pytest
from textual.widgets import Input, ListView, Static, ListItem, Label, ContentSwitcher
from ytune.app import YTune, Sidebar, TrackItem
from ytune.models import Track
from unittest.mock import MagicMock
from pathlib import Path

@pytest.fixture
def mock_deps(mocker):
    """Fixture to mock all external dependencies."""
    mock_api = mocker.patch("ytune.app.YTuneAPI")
    mock_player_class = mocker.patch("ytune.app.Player")
    mock_db = mocker.patch("ytune.app.db")
    
    mock_player = mock_player_class.return_value
    mock_player.duration = 100.0
    mock_player.position = 0.0
    
    return {
        "api": mock_api.return_value,
        "player": mock_player,
        "db": mock_db
    }

@pytest.mark.asyncio
async def test_wishlist_binding_saves_to_db(mock_deps):
    app = YTune()
    async with app.run_test() as pilot:
        # Set a current track
        track = Track(videoId="vid1", title="Save Me", artist="Artist")
        app.play_track(track)
        
        # Press 'w'
        await pilot.press("w")
        
        # Verify db was called
        mock_deps["db"].add_to_wishlist.assert_called_once_with(
            app.db_conn, "vid1", "Save Me", "Artist"
        )

@pytest.mark.asyncio
async def test_navigation_switches_view(mock_deps):
    app = YTune()
    async with app.run_test() as pilot:
        sidebar_list = app.query_one("#sidebar-nav", ListView)
        
        # Manually trigger selection with correct arguments
        event = ListView.Selected(sidebar_list, sidebar_list.children[2], index=2)
        await app.handle_nav(event)
        
        # Verify ContentSwitcher changed
        switcher = app.query_one(ContentSwitcher)
        assert switcher.current == "view-wishlist"
        
        # Verify db was queried to refresh wishlist
        mock_deps["db"].get_wishlist.assert_called_once()

@pytest.mark.asyncio
async def test_auto_mix_on_track_end(mock_deps):
    # Mock radio recommendations
    mock_deps["api"].get_track_radio.return_value = [
        Track(videoId="next1", title="Radio Next", artist="Radio Artist")
    ]
    
    app = YTune()
    async with app.run_test() as pilot:
        # Set current track
        app.current_track = Track(videoId="current", title="Now playing", artist="Now artist")
        
        # Simulate track end
        app.handle_track_end()
        
        # Give worker time to fetch and call_from_thread
        await pilot.pause(1.0)
        
        # Verify player played the recommended track
        mock_deps["player"].play.assert_called_with("next1")
        assert app.current_track.video_id == "next1"

@pytest.mark.asyncio
async def test_search_results_mapping(mock_deps):
    app = YTune()
    async with app.run_test() as pilot:
        # Direct call to display_results to verify mapping without background worker timing issues
        tracks = [Track(videoId="vid1", title="Song 1", artist="Artist 1")]
        await app.display_results(tracks)
        
        results_list = app.query_one("#results-list", ListView)
        assert len(results_list.children) == 1
        item = results_list.children[0]
        assert isinstance(item, TrackItem)
        # Access the label within the TrackItem (ListItem)
        label = item.query_one(Label)
        assert "Song 1 - Artist 1" in str(label.render())
