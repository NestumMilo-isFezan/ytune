import sqlite3
from pathlib import Path
from typing import Optional, List, Tuple

DEFAULT_DB_PATH = Path.home() / ".config" / "ytune" / "ytune.db"

def init_db(db_path: Optional[Path] = None):
    path = db_path or DEFAULT_DB_PATH
    if path != Path(":memory:"):
        path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(path), check_same_thread=False)
    cursor = conn.cursor()
    
    # Wishlist tracks
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wishlist (
      id INTEGER PRIMARY KEY,
      video_id TEXT NOT NULL UNIQUE,
      title TEXT,
      artist TEXT,
      added_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    # Wishlist playlists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wishlist_playlists (
      id INTEGER PRIMARY KEY,
      playlist_id TEXT NOT NULL UNIQUE,
      title TEXT,
      start_mix_after INTEGER DEFAULT 0,
      added_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    # Playback history
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
      id INTEGER PRIMARY KEY,
      video_id TEXT NOT NULL,
      title TEXT,
      artist TEXT,
      played_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    # App settings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
      key TEXT PRIMARY KEY,
      value TEXT
    )""")
    
    conn.commit()
    return conn

def add_to_wishlist(conn, video_id: str, title: str, artist: str):
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO wishlist (video_id, title, artist) VALUES (?, ?, ?)", 
                       (video_id, title, artist))
        conn.commit()
    except sqlite3.Error:
        pass

def remove_from_wishlist(conn, video_id: str):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wishlist WHERE video_id = ?", (video_id,))
    conn.commit()

def get_wishlist(conn) -> List[Tuple[str, str, str]]:
    cursor = conn.cursor()
    cursor.execute("SELECT video_id, title, artist FROM wishlist ORDER BY added_at DESC")
    return cursor.fetchall()

def add_to_history(conn, video_id: str, title: str, artist: str):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO history (video_id, title, artist) VALUES (?, ?, ?)", 
                   (video_id, title, artist))
    conn.commit()

def get_history(conn, limit: int = 50) -> List[Tuple[str, str, str]]:
    cursor = conn.cursor()
    cursor.execute("SELECT video_id, title, artist FROM history ORDER BY played_at DESC LIMIT ?", (limit,))
    return cursor.fetchall()

def get_forgotten_favourites(conn, days: int = 90) -> List[Tuple[str, str, str]]:
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT video_id, title, artist FROM history 
        WHERE played_at < datetime('now', '-{days} days')
        AND video_id NOT IN (
            SELECT video_id FROM history WHERE played_at >= datetime('now', '-{days} days')
        )
        GROUP BY video_id
        ORDER BY played_at DESC
    """)
    return cursor.fetchall()

if __name__ == "__main__":
    init_db()
