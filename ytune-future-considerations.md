# ytune Future Considerations

This document tracks "pro" features and enhancements to be considered after the core functionality is stable.

## 🎨 Visual Enhancements
- **Album Art Support:** Integrate Sixel or Kitty protocol support via `textual-imageview` or raw `mpv` embedding to display high-quality cover art in the TUI.
- **Dynamic Theming:** Implement a theme engine that changes the TUI's primary and accent colors based on the current track's album art palette.
- **Custom CSS:** Allow users to provide a `custom.tcss` file for deep UI personalization.

## 🎵 Audio & Metadata
- **Lyrics Integration:**
    - Fetch synced/unsynced lyrics via `ytmusicapi`.
    - Fallback to `lrclib` or `syncedlyrics` for missing tracks.
    - Add a dedicated "Lyrics" view in the main content area.
- **Last.fm Scrobbling:** Add optional scrobbling support using `pylast`.
- **Local Audio Caching:** Implement a local cache in `~/.cache/ytune/tracks/` to reduce bandwidth usage on repeat listens and support offline playback of the wishlist.
- **High-Fidelity Mode:** Option to force `opus` or `m4a` formats via `yt-dlp` for audiophiles.

## 🛰️ Integrations
- **Desktop Notifications:** Send system-level notifications (Title, Artist, Thumbnail) on track changes using `notify2` or `plyer`.
- **Discord Rich Presence:** Show the current playing track and artist in Discord status via `pypresence`.
- **MPRIS Support:** Implement the MPRIS D-Bus interface to allow controlling `ytune` via system media keys and widgets (Linux).

## 🛠️ Performance & UX
- **Zero-Gap Playback:** Use a dual-`mpv` instance or pre-buffering strategy to eliminate silence between tracks.
- **Remote Control API:** Expose a simple local socket or HTTP API to control the player externally (e.g., from a mobile app or custom script).
- **Search Auto-complete:** Provide real-time search suggestions as the user types in the search bar.
