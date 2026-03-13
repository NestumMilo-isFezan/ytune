# ytune — TUI YouTube Music Client

A terminal-based YouTube Music client with ad-free playback, Google account integration, smart recommendations, and a wishlist system.

---

## Stack

| Layer | Library |
|---|---|
| Language | Python 3.11+ |
| Auth + Data | `ytmusicapi` (browser cookie auth) |
| Audio extraction | `yt-dlp` |
| Playback | `mpv` via `python-mpv` |
| TUI | `textual` |
| Persistence | `sqlite3` (built-in) |

---

## TUI Layout

Inspired by opencode / claude code — sidebar navigation, scrollable main content, persistent player bar at bottom.

```
┌─────────────────────────────────────────────────────────────┐
│   ytune                                    [?] help  [q] quit │
├──────────────┬──────────────────────────────────────────────┤
│              │  🏠 Home                                      │
│  Home        │                                               │
│  Search      │  ▶ Start Listening                           │
│  Wishlist    │  ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  Library     │  │ track    │ │ track    │ │ track    │    │
│  History     │  └──────────┘ └──────────┘ └──────────┘    │
│              │                                               │
│              │  🎬 Music Videos                             │
│              │  ...                                          │
│              │                                               │
│              │  💿 Recent Albums                            │
│              │  ...                                          │
│              │                                               │
│              │  ✨ Forgotten Favourites                     │
│              │  ...                                          │
├──────────────┴──────────────────────────────────────────────┤
│  ♪ Track Name — Artist          ██████░░░░  2:14 / 4:32    │
│  [space] pause  [n] next  [p] prev  [w] wishlist  [/] search│
└─────────────────────────────────────────────────────────────┘
```

---

## Features

### Homepage

- **Start Listening** — recently played tracks, resume from last position
- **Music Videos** — video-flagged tracks (audio-only playback in TUI)
- **Recent Albums** — from artists in your listening history
- **Forgotten Favourites** — liked/played tracks not heard in 3+ months

### Playback

- Ad-free audio streaming via `yt-dlp` + `mpv`
- Fast buffering — preload next track in queue
- Controls: pause, skip, previous, seek, volume

### Google Account Integration

- Auth via browser cookies (no OAuth setup) using `ytmusicapi`
- Access liked songs, personal playlists, listening history
- Pull recommendations from YT Music radio/mix

### Wishlist

- Save tracks and playlists to wishlist
- Set a "start mix after" target — auto-queue after wishlist finishes
- Auto-play similar genre based on entire wishlist when queue ends
- Stored in local `sqlite` database

### Recommendations

- Track radio based on currently playing song
- Genre similarity scoring across wishlist tracks
- Seamless auto-mix when wishlist ends

---

## Keyboard Shortcuts

| Key | Action |
|---|---|
| `space` | Pause / resume |
| `n` | Next track |
| `p` | Previous track |
| `w` | Add to wishlist |
| `/` | Search |
| `q` | Quit |
| `?` | Help |
| `↑ ↓` | Navigate lists |
| `enter` | Select / play |

---

## Database Schema (sqlite)

```sql
-- Wishlist tracks
CREATE TABLE wishlist (
  id INTEGER PRIMARY KEY,
  video_id TEXT NOT NULL,
  title TEXT,
  artist TEXT,
  added_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Wishlist playlists
CREATE TABLE wishlist_playlists (
  id INTEGER PRIMARY KEY,
  playlist_id TEXT NOT NULL,
  title TEXT,
  start_mix_after INTEGER DEFAULT 0, -- boolean
  added_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Playback history (for forgotten favourites)
CREATE TABLE history (
  id INTEGER PRIMARY KEY,
  video_id TEXT NOT NULL,
  title TEXT,
  artist TEXT,
  played_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- App settings
CREATE TABLE settings (
  key TEXT PRIMARY KEY,
  value TEXT
);
```

---

## Build Phases

### Phase 1 — Playback Core *(1–2 days)*
- `ytmusicapi` browser auth setup
- Search a song, extract audio URL via `yt-dlp`
- Play with `mpv`, basic controls in terminal (no TUI yet)

### Phase 2 — TUI Shell *(2–3 days)*
- `textual` layout: sidebar, main panel, player bar
- Keyboard shortcuts wired up
- Search → add to queue → play flow working

### Phase 2.5 — Homepage *(1–2 days)*
- Pull real data for all 4 homepage sections from `ytmusicapi`
- Forgotten Favourites logic using local history + timestamp diff

### Phase 3 — Wishlist *(1–2 days)*
- sqlite schema and CRUD
- Add/remove from wishlist in TUI
- "Start mix after" toggle per playlist

### Phase 4 — Recommendations + Auto-mix *(2–3 days)*
- YT Music radio pull based on current track
- Genre similarity across wishlist metadata
- Auto-queue when wishlist finishes

### Phase 5 — Polish *(ongoing)*
- Preload next track for zero-gap playback
- Album art via sixel/kitty protocol (terminal-dependent)
- Config file (`~/.config/ytune/config.toml`)
- Proper error handling for network failures

---

## Notes

- `ytmusicapi` browser auth: run `ytmusicapi browser` once to set up, saves cookies to `~/.config/ytune/auth.json`
- `yt-dlp` format: use `bestaudio` to minimise buffer time
- `mpv` socket: use `--input-ipc-server` for programmatic control from Python
- Forgotten Favourites threshold: configurable, default 90 days
