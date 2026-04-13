import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "cinebud.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_genres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            genre_id INTEGER NOT NULL,
            genre_name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            UNIQUE(user_id, genre_id)
        );

        CREATE TABLE IF NOT EXISTS user_titles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tmdb_id INTEGER NOT NULL,
            media_type TEXT NOT NULL CHECK(media_type IN ('movie', 'tv')),
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            UNIQUE(user_id, tmdb_id, media_type)
        );

        CREATE TABLE IF NOT EXISTS title_state (
            tmdb_id INTEGER NOT NULL,
            media_type TEXT NOT NULL,
            last_known_state TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (tmdb_id, media_type)
        );

        CREATE TABLE IF NOT EXISTS notification_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tmdb_id INTEGER NOT NULL,
            media_type TEXT NOT NULL,
            event_type TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            UNIQUE(user_id, tmdb_id, media_type, event_type)
        );
    """)

    conn.commit()
    conn.close()