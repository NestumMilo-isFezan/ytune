from ytmusicapi import YTMusic
from pathlib import Path
from typing import List, Optional
from .models import Track, Album, Playlist

class YTuneAPI:
    def __init__(self, auth_path: Optional[str] = None):
        if auth_path is None:
            auth_path = str(Path.home() / ".config" / "ytune" / "auth.json")
        
        # Initialize YTMusic. If auth file doesn't exist, it operates in guest mode.
        # Guest mode allows searching but not library/history access.
        try:
            self.yt = YTMusic(auth_path if Path(auth_path).exists() else None)
        except Exception:
            self.yt = YTMusic()

    def search_tracks(self, query: str, limit: int = 20) -> List[Track]:
        """Search for songs and return a list of Track models."""
        results = self.yt.search(query, filter="songs", limit=limit)
        tracks = []
        for res in results:
            try:
                # ytmusicapi returns nested artists, we flatten for our model
                if 'artists' in res and isinstance(res['artists'], list):
                    res['artist'] = ", ".join([a['name'] for a in res['artists']])
                
                # Thumbnails are a list, we take the last (usually highest res)
                if 'thumbnails' in res and isinstance(res['thumbnails'], list):
                    res['thumbnailUrl'] = res['thumbnails'][-1]['url']
                
                tracks.append(Track.model_validate(res))
            except Exception:
                continue
        return tracks

    def get_track_radio(self, video_id: str, limit: int = 10) -> List[Track]:
        """Get recommended tracks based on a video_id (Watch Playlist)."""
        try:
            watch_playlist = self.yt.get_watch_playlist(videoId=video_id, limit=limit)
            tracks = []
            for res in watch_playlist.get('tracks', []):
                try:
                    # Same flattening as search
                    if 'artists' in res and isinstance(res['artists'], list):
                        res['artist'] = ", ".join([a['name'] for a in res['artists']])
                    if 'thumbnails' in res and isinstance(res['thumbnails'], list):
                        res['thumbnailUrl'] = res['thumbnails'][-1]['url']
                        
                    tracks.append(Track.model_validate(res))
                except Exception:
                    continue
            return tracks
        except Exception:
            return []

    def get_home_data(self):
        """Fetch raw home data to be processed by the UI."""
        try:
            return self.yt.get_home(limit=10)
        except Exception:
            return []

if __name__ == "__main__":
    # Quick Test
    api = YTuneAPI()
    print("Searching for 'Rick Astley'...")
    results = api.search_tracks("Rick Astley", limit=3)
    for t in results:
        print(f" - {t.title} by {t.artist} [{t.video_id}]")
