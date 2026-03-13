from pathlib import Path

import pytest

from ytune.db import (
    add_to_history,
    add_to_wishlist,
    get_forgotten_favourites,
    get_history,
    get_wishlist,
    init_db,
    remove_from_wishlist,
)


@pytest.fixture
def db_conn():
    conn = init_db(Path(":memory:"))
    yield conn
    conn.close()

def test_wishlist_crud(db_conn):
    add_to_wishlist(db_conn, "vid1", "Title 1", "Artist 1")
    add_to_wishlist(db_conn, "vid2", "Title 2", "Artist 2")
    
    wishlist = get_wishlist(db_conn)
    assert len(wishlist) == 2
    
    remove_from_wishlist(db_conn, "vid1")
    wishlist = get_wishlist(db_conn)
    assert len(wishlist) == 1
    assert wishlist[0][0] == "vid2"

def test_history_logging(db_conn):
    add_to_history(db_conn, "vid1", "Title 1", "Artist 1")
    add_to_history(db_conn, "vid1", "Title 1", "Artist 1") # Play twice
    
    history = get_history(db_conn)
    assert len(history) == 2
    assert history[0][0] == "vid1"

def test_forgotten_favourites(db_conn):
    cursor = db_conn.cursor()
    # Insert a track played 100 days ago
    cursor.execute("""
        INSERT INTO history (video_id, title, artist, played_at) 
        VALUES ('oldie', 'Old Song', 'Old Artist', datetime('now', '-100 days'))
    """)
    # Insert a track played 10 days ago
    cursor.execute("""
        INSERT INTO history (video_id, title, artist, played_at) 
        VALUES ('recent', 'New Song', 'New Artist', datetime('now', '-10 days'))
    """)
    db_conn.commit()
    
    forgotten = get_forgotten_favourites(db_conn, days=90)
    assert len(forgotten) == 1
    assert forgotten[0][0] == "oldie"
    
    # If we play the oldie again today, it should NOT be forgotten
    add_to_history(db_conn, "oldie", "Old Song", "Old Artist")
    forgotten = get_forgotten_favourites(db_conn, days=90)
    assert len(forgotten) == 0

def test_db_threading(db_conn):
    import threading
    
    def worker(conn):
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        return cursor.fetchone()
    
    # Run the worker in a separate thread and ensure it doesn't raise ProgrammingError
    result = []
    thread = threading.Thread(target=lambda: result.append(worker(db_conn)))
    thread.start()
    thread.join()
    
    assert result == [(1,)]
