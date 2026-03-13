# ytune Implementation Plan

This document outlines the step-by-step execution plan for building the `ytune` TUI YouTube Music client.

## Current Status: ✅ Scaffolding Complete
- [x] Project structure initialized with `pixi`.
- [x] Core dependencies installed (`textual`, `ytmusicapi`, `yt-dlp`, `python-mpv`).
- [x] TUI skeleton with sidebar and player bar (`app.py`).
- [x] Database schema defined (`db.py`).
- [x] Entry point created (`main.py`).

---

## Phase 1: Playback Core (The "Engine") ✅
**Goal:** Successfully stream audio from a YouTube URL using `yt-dlp` and `mpv`.

- [x] **1.1. Audio Extraction (`player.py`):** Implement `yt-dlp` wrapper to fetch the `bestaudio` URL for a given `video_id`.
- [x] **1.2. mpv Integration (`player.py`):** Initialize `python-mpv` and implement `play(url)`, `pause()`, `stop()`, and `seek()`.
- [x] **1.3. Event Handling:** Set up callbacks for "end of track" to support queueing.
- [x] **1.4. CLI Test:** Create a small script to verify `pixi run python src/ytune/player.py <video_id>` plays audio.

## Phase 2: YouTube Music API & Data ✅
**Goal:** Connect to YouTube Music and fetch real data.

- [x] **2.1. Auth Setup:** Instructions for the user to run `ytmusicapi browser` and store `auth.json`.
- [x] **2.2. API Wrapper (`api.py`):**
    - `search(query)`: Return list of tracks.
    - `get_home()`: Fetch the 4 homepage sections.
    - `get_track_radio(video_id)`: For recommendations.
- [x] **2.3. Data Models (`models.py`):** Define Pydantic models for `Track`, `Album`, and `Playlist` for type-safe data handling.

## Phase 2.5: Unit Testing & Reliability ✅
**Goal:** Ensure the core logic is robust and verified.

- [x] **2.5.1. Testing Infrastructure:** Set up `pytest` and `pytest-mock`.
- [x] **2.5.2. Core Unit Tests:** Implement tests for `models.py`, `api.py`, `db.py`, and `player.py`.
- [x] **2.5.3. CI-Ready:** Ensure all tests pass with `pixi run pytest`.
- [x] **2.5.4. TUI Interaction Tests:** Implement tests for search, selection, and playback controls in `app.py`.

## Phase 3: TUI & Playback Integration ✅
**Goal:** Make the UI interactive and functional.

- [x] **3.1. Navigation Logic:** Switch main content area based on sidebar selection.
- [x] **3.2. Search Implementation:** Add a search overlay/input that populates a list of results.
- [x] **3.3. Player Controller:** Connect the `PlayerBar` in the TUI to the `player.py` engine.
- [x] **3.4. Progress Bar:** Update the UI progress bar in real-time as the track plays.

## Phase 4: Persistence & Wishlist ✅
**Goal:** Implement the local database features.

- [x] **4.1. DB Helpers (`db.py`):** Implement functions to add/remove tracks from the wishlist and record history.
- [x] **4.2. Wishlist View:** Create a TUI screen to display and play from the local wishlist.
- [x] **4.3. History Tracking:** Automatically log played tracks to the `history` table.
- [x] **4.4. Forgotten Favourites:** Implement the logic to filter history for tracks not heard in >90 days.

## Phase 5: Recommendations & Advanced Features ✅
**Goal:** Smart queueing and polish.

- [x] **5.1. Auto-Mix Engine:** Logic to fetch "radio" tracks when the current queue or wishlist ends.
- [x] **5.2. Preloading:** Integrated basic auto-mix for seamless playback.
- [x] **5.3. Configuration:** Basic setup with auth.json and database persistence.
- [x] **5.4. Error Handling:** Graceful handling for missing libmpv and network errors.

---

## Final Summary
`ytune` is now a fully functional terminal-based YouTube Music client with:
- ✅ Audio streaming via `yt-dlp` and `mpv`.
- ✅ Textual TUI with Sidebar, Search, Home, Wishlist, and History views.
- ✅ YouTube Music integration for search, home data, and radio.
- ✅ Local SQLite persistence for history and wishlist.
- ✅ Auto-mix logic for infinite playback.
- ✅ Comprehensive unit and TUI interaction tests.

