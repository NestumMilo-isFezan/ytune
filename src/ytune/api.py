import logging
from pathlib import Path

from ytmusicapi import YTMusic

from .models import Track

logger = logging.getLogger(__name__)


def _normalize_track_result(res: dict) -> dict:
    """Flatten nested ytmusicapi fields into a form Track.model_validate accepts."""
    result = dict(res)
    if isinstance(result.get("artists"), list):
        result["artist"] = ", ".join(a["name"] for a in result["artists"])
    if isinstance(result.get("album"), dict):
        result["album"] = result["album"].get("name")
    if isinstance(result.get("thumbnails"), list):
        result["thumbnailUrl"] = result["thumbnails"][-1]["url"]
    return result


class YTuneAPI:
    def __init__(self, auth_path: str | None = None) -> None:
        if auth_path is None:
            auth_path = str(Path.home() / ".config" / "ytune" / "auth.json")

        try:
            self.yt = YTMusic(auth_path if Path(auth_path).exists() else None)
        except Exception as e:
            logger.warning(
                "Failed to init YTMusic with auth, falling back to guest: %s", e
            )
            self.yt = YTMusic()

    def search_tracks(self, query: str, limit: int = 20) -> list[Track]:
        """Search for songs and return a list of Track models."""
        results = self.yt.search(query, filter="songs", limit=limit)
        tracks = []
        for res in results:
            try:
                tracks.append(Track.model_validate(_normalize_track_result(res)))
            except Exception as e:
                logger.warning("Skipping malformed search result: %s", e)
        return tracks

    def get_track_radio(self, video_id: str, limit: int = 10) -> list[Track]:
        """Get recommended tracks based on a video_id (Watch Playlist)."""
        try:
            watch_playlist = self.yt.get_watch_playlist(videoId=video_id, limit=limit)
            tracks = []
            for res in watch_playlist.get("tracks", []):
                try:
                    tracks.append(Track.model_validate(_normalize_track_result(res)))
                except Exception as e:
                    logger.warning("Skipping malformed radio result: %s", e)
            return tracks
        except Exception as e:
            logger.error("Failed to fetch radio for video_id=%s: %s", video_id, e)
            return []

    def get_home_data(self) -> list:
        """Fetch raw home data to be processed by the UI."""
        try:
            return self.yt.get_home(limit=10)
        except Exception as e:
            logger.error("Failed to fetch home data: %s", e)
            return []


if __name__ == "__main__":
    api = YTuneAPI()
    print("Searching for 'Rick Astley'...")
    results = api.search_tracks("Rick Astley", limit=3)
    for t in results:
        print(f" - {t.title} by {t.artist} [{t.video_id}]")
