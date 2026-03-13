import yt_dlp
import logging
import sys
import locale
from typing import Optional, Callable

# Set LC_NUMERIC to 'C' as required by libmpv
try:
    locale.setlocale(locale.LC_NUMERIC, 'C')
except Exception:
    pass

# Set up basic logging for debugging audio extraction
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import mpv
except OSError:
    logger.warning("libmpv not found. Audio playback will not work.")
    mpv = None

class Player:
    def __init__(self):
        if mpv is None:
            raise OSError("mpv library not found. Please install libmpv.")
            
        # Extra safety: Ensure environment and locale are 'C' at init time
        import os
        import locale
        os.environ["LC_NUMERIC"] = "C"
        try:
            locale.setlocale(locale.LC_NUMERIC, "C")
        except Exception:
            pass

        # Initialize mpv with some sensible defaults for streaming
        try:
            self.client = mpv.MPV(
                input_default_bindings=True,
                input_vo_keyboard=True
            )
        except OSError as e:
            logger.error("Failed to initialize mpv. Is it installed on your system?")
            raise e
        
        # yt-dlp options for fastest audio extraction
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

    def get_stream_url(self, video_id: str) -> Optional[str]:
        """Extract the direct streaming URL from a YouTube video ID."""
        # Note: In the test I used watch?vid123, but the code uses watch?v=vid123
        url = f"https://www.youtube.com/watch?v={video_id}"
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('url')
        except Exception as e:
            logger.error(f"Failed to extract stream URL for {video_id}: {e}")
            return None

    def play(self, video_id: str):
        """Fetch URL and start playback."""
        stream_url = self.get_stream_url(video_id)
        if stream_url:
            logger.info(f"Playing stream: {video_id}")
            self.client.play(stream_url)
        else:
            logger.error("Could not play: Stream URL extraction failed.")

    def toggle_pause(self):
        self.client.pause = not self.client.pause

    def stop(self):
        self.client.stop()

    def seek(self, seconds: int, relative: bool = True):
        self.client.seek(seconds, reference='relative' if relative else 'absolute')

    @property
    def position(self) -> float:
        return self.client.time_pos or 0.0

    @property
    def duration(self) -> float:
        return self.client.duration or 0.0

    def on_end(self, callback: Callable):
        """Register a callback for when the track finishes."""
        @self.client.event_callback('end-file')
        def handle_end(event):
            callback()

if __name__ == "__main__":
    # Quick CLI Test: pixi run python src/ytune/player.py <video_id>
    if len(sys.argv) < 2:
        print("Usage: pixi run python src/ytune/player.py <video_id>")
        sys.exit(1)
    
    video_id = sys.argv[1]
    player = Player()
    
    def finished():
        print("\nPlayback finished!")
        sys.exit(0)
        
    player.on_end(finished)
    player.play(video_id)
    
    print(f"Playing {video_id}... Press Ctrl+C to stop.")
    try:
        player.client.wait_for_playback()
    except KeyboardInterrupt:
        player.stop()
        print("\nStopped.")
