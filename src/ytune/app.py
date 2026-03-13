import logging

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.message import Message
from textual.widgets import (
    ContentSwitcher,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    ProgressBar,
    Static,
)

from . import db
from .api import YTuneAPI
from .models import Track
from .player import Player

logger = logging.getLogger(__name__)


class TrackItem(ListItem):
    """Custom ListItem to hold track data."""

    def __init__(self, track: Track) -> None:
        super().__init__(Label(f"{track.title} - {track.artist}"))
        self.track_data = track


class Sidebar(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Label("ytune", id="app-title")
        yield ListView(
            ListItem(Label("🏠 Home"), id="nav-home"),
            ListItem(Label("🔍 Search"), id="nav-search"),
            ListItem(Label("❤️ Wishlist"), id="nav-wishlist"),
            ListItem(Label("🕒 History"), id="nav-history"),
            id="sidebar-nav",
        )


class PlayerBar(Horizontal):
    def compose(self) -> ComposeResult:
        with Horizontal(id="player-info-container"):
            yield Static("♪ Not Playing", id="track-info")
            yield ProgressBar(total=100, show_eta=False, id="track-progress")


class YTune(App):
    class SearchResultsReady(Message):
        """Posted from the search worker when results are available."""

        def __init__(self, results: list) -> None:
            super().__init__()
            self.results = results

    CSS = """
    Sidebar {
        width: 25;
        background: $panel;
        border-right: tall $primary;
        padding: 1;
    }
    
    #app-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
        color: $accent;
    }

    #main-container {
        padding: 1;
    }

    .search-input {
        margin-bottom: 1;
    }

    .view-title {
        text-style: bold;
        margin-top: 1;
        margin-bottom: 1;
        color: $primary;
    }

    PlayerBar {
        height: 3;
        dock: bottom;
        background: $accent;
        color: $text;
        padding: 1;
    }

    #player-info-container {
        width: 100%;
        align: center middle;
    }

    #track-info {
        width: 40%;
        content-align: left middle;
    }

    #track-progress {
        width: 60%;
    }

    ListView {
        background: transparent;
        height: auto;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("space", "toggle_play", "Pause/Resume"),
        Binding("/", "focus_search", "Search"),
        Binding("w", "add_to_wishlist", "Add to Wishlist"),
        Binding("n", "skip_track", "Next"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.api = YTuneAPI()
        try:
            self.player: Player | None = Player()
        except OSError:
            self.player = None
        self.current_track: Track | None = None
        self.db_conn = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Sidebar()
            with Container(id="main-container"):
                with ContentSwitcher(initial="view-home"):
                    with VerticalScroll(id="view-home"):
                        yield Label("🏠 Home", classes="view-title")
                        yield Label("Start Listening", classes="view-subtitle")
                        yield ListView(id="home-start-listening")
                        yield Label("Forgotten Favourites", classes="view-subtitle")
                        yield ListView(id="home-forgotten")
                    with VerticalScroll(id="view-search"):
                        yield Input(
                            placeholder="Search for songs...",
                            classes="search-input",
                            id="search-input",
                        )
                        yield ListView(id="results-list")
                    with VerticalScroll(id="view-wishlist"):
                        yield Label("❤️ Your Wishlist", classes="view-title")
                        yield ListView(id="wishlist-list")
                    with VerticalScroll(id="view-history"):
                        yield Label("🕒 Recently Played", classes="view-title")
                        yield ListView(id="history-list")
        yield PlayerBar()
        yield Footer()

    def on_mount(self) -> None:
        self.db_conn = db.init_db()
        if self.player:
            self.player.on_end(self.handle_track_end)
        self.set_interval(1.0, self.update_progress)
        self.fetch_home_content()

    def on_unmount(self) -> None:
        if self.db_conn:
            self.db_conn.close()

    def handle_track_end(self) -> None:
        """Called when a track finishes playing."""
        self.call_from_thread(self.action_skip_track)

    def update_progress(self) -> None:
        if self.player and self.player.duration > 0:
            progress = (self.player.position / self.player.duration) * 100
            self.query_one("#track-progress", ProgressBar).progress = progress

    @on(ListView.Selected, "#sidebar-nav")
    async def handle_nav(self, event: ListView.Selected) -> None:
        """Handle sidebar navigation."""
        nav_id = event.item.id
        switcher = self.query_one(ContentSwitcher)

        if nav_id == "nav-home":
            switcher.current = "view-home"
            self.fetch_home_content()
        elif nav_id == "nav-search":
            switcher.current = "view-search"
            self.query_one("#search-input").focus()
        elif nav_id == "nav-wishlist":
            switcher.current = "view-wishlist"
            await self.refresh_wishlist()
        elif nav_id == "nav-history":
            switcher.current = "view-history"
            await self.refresh_history()

    async def refresh_wishlist(self) -> None:
        wishlist_data = db.get_wishlist(self.db_conn)
        wishlist_list = self.query_one("#wishlist-list", ListView)
        wishlist_list.clear()
        for vid, title, artist in wishlist_data:
            await wishlist_list.mount(
                TrackItem(Track(videoId=vid, title=title, artist=artist))
            )

    async def refresh_history(self) -> None:
        history_data = db.get_history(self.db_conn)
        history_list = self.query_one("#history-list", ListView)
        history_list.clear()
        for vid, title, artist in history_data:
            await history_list.mount(
                TrackItem(Track(videoId=vid, title=title, artist=artist))
            )

    @work(exclusive=True, thread=True)
    def fetch_home_content(self) -> None:
        forgotten = db.get_forgotten_favourites(self.db_conn)
        home_data = self.api.get_home_data()
        self.call_from_thread(self.display_home_content, forgotten, home_data)

    def display_home_content(self, forgotten: list, home_data: list) -> None:
        forgotten_list = self.query_one("#home-forgotten", ListView)
        forgotten_list.clear()
        for vid, title, artist in forgotten[:10]:
            forgotten_list.append(
                TrackItem(Track(videoId=vid, title=title, artist=artist))
            )

        start_list = self.query_one("#home-start-listening", ListView)
        start_list.clear()
        for section in home_data:
            if "contents" in section:
                for item in section["contents"][:10]:
                    if "videoId" in item:
                        try:
                            if "artists" in item:
                                item["artist"] = ", ".join(
                                    [a["name"] for a in item["artists"]]
                                )
                            track = Track.model_validate(item)
                            start_list.append(TrackItem(track))
                        except Exception as e:
                            logger.warning("Skipping malformed home item: %s", e)

    @on(Input.Submitted, "#search-input")
    def handle_search(self, event: Input.Submitted) -> None:
        self.perform_search(event.value)

    @work(exclusive=True, thread=True)
    def perform_search(self, query: str) -> None:
        results = self.api.search_tracks(query)
        self.post_message(self.SearchResultsReady(results))

    async def on_ytune_search_results_ready(self, event: SearchResultsReady) -> None:
        results_list = self.query_one("#results-list", ListView)
        results_list.clear()
        for track in event.results:
            await results_list.mount(TrackItem(track))

    @on(ListView.Selected)
    def handle_selection(self, event: ListView.Selected) -> None:
        if isinstance(event.item, TrackItem):
            self.play_track(event.item.track_data)

    def play_track(self, track: Track) -> None:
        self.current_track = track
        if self.player:
            self.player.play(track.video_id)
        db.add_to_history(self.db_conn, track.video_id, track.title, track.artist)
        self.query_one("#track-info", Static).update(
            f"♪ {track.title} — {track.artist}"
        )
        self.query_one("#track-progress", ProgressBar).progress = 0

    def action_skip_track(self) -> None:
        if self.current_track:
            self.fetch_and_play_radio(self.current_track.video_id)

    @work(exclusive=True, thread=True)
    def fetch_and_play_radio(self, video_id: str) -> None:
        recommendations = self.api.get_track_radio(video_id, limit=5)
        if recommendations:
            self.call_from_thread(self.play_track, recommendations[0])

    def action_add_to_wishlist(self) -> None:
        if self.current_track:
            db.add_to_wishlist(
                self.db_conn,
                self.current_track.video_id,
                self.current_track.title,
                self.current_track.artist,
            )
            self.notify(f"Added to Wishlist: {self.current_track.title}")

    def action_toggle_play(self) -> None:
        if self.player:
            self.player.toggle_pause()

    def action_focus_search(self) -> None:
        self.query_one(ContentSwitcher).current = "view-search"
        self.query_one("#search-input").focus()


if __name__ == "__main__":
    app = YTune()
    app.run()
