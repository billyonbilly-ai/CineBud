import json
from db.database import get_connection


# Users

def upsert_user(user_id: int, username: str, first_name: str):
    conn = get_connection()
    conn.execute("""
        INSERT INTO users (user_id, username, first_name)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name
    """, (user_id, username, first_name))
    conn.commit()
    conn.close()


def get_all_user_ids() -> list[int]:
    conn = get_connection()
    rows = conn.execute("SELECT user_id FROM users").fetchall()
    conn.close()
    return [row["user_id"] for row in rows]


# Genres

def save_user_genres(user_id: int, genres: list[dict]):
    """genres: [{"genre_id": 28, "genre_name": "Action"}, ...]"""
    conn = get_connection()
    conn.execute("DELETE FROM user_genres WHERE user_id = ?", (user_id,))
    conn.executemany("""
        INSERT INTO user_genres (user_id, genre_id, genre_name)
        VALUES (?, ?, ?)
    """, [(user_id, g["genre_id"], g["genre_name"]) for g in genres])
    conn.commit()
    conn.close()


def get_user_genres(user_id: int) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT genre_id, genre_name FROM user_genres WHERE user_id = ?",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_users_with_genre(genre_id: int) -> list[int]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT user_id FROM user_genres WHERE genre_id = ?", (genre_id,)
    ).fetchall()
    conn.close()
    return [row["user_id"] for row in rows]


# Specific Titles

def add_user_title(user_id: int, tmdb_id: int, media_type: str, title: str):
    conn = get_connection()
    conn.execute("""
        INSERT OR IGNORE INTO user_titles (user_id, tmdb_id, media_type, title)
        VALUES (?, ?, ?, ?)
    """, (user_id, tmdb_id, media_type, title))
    conn.commit()
    conn.close()


def remove_user_title(user_id: int, tmdb_id: int, media_type: str):
    conn = get_connection()
    conn.execute("""
        DELETE FROM user_titles
        WHERE user_id = ? AND tmdb_id = ? AND media_type = ?
    """, (user_id, tmdb_id, media_type))
    conn.commit()
    conn.close()


def get_user_titles(user_id: int) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT tmdb_id, media_type, title FROM user_titles WHERE user_id = ?",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_tracked_titles() -> list[dict]:
    """Returns all unique titles being tracked across all users."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT DISTINCT tmdb_id, media_type, title FROM user_titles
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_users_tracking_title(tmdb_id: int, media_type: str) -> list[int]:
    conn = get_connection()
    rows = conn.execute("""
        SELECT user_id FROM user_titles
        WHERE tmdb_id = ? AND media_type = ?
    """, (tmdb_id, media_type)).fetchall()
    conn.close()
    return [row["user_id"] for row in rows]


# Title State

def get_title_state(tmdb_id: int, media_type: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("""
        SELECT last_known_state FROM title_state
        WHERE tmdb_id = ? AND media_type = ?
    """, (tmdb_id, media_type)).fetchone()
    conn.close()
    if row and row["last_known_state"]:
        return json.loads(row["last_known_state"])
    return None


def set_title_state(tmdb_id: int, media_type: str, state: dict):
    conn = get_connection()
    conn.execute("""
        INSERT INTO title_state (tmdb_id, media_type, last_known_state, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(tmdb_id, media_type) DO UPDATE SET
            last_known_state = excluded.last_known_state,
            updated_at = CURRENT_TIMESTAMP
    """, (tmdb_id, media_type, json.dumps(state)))
    conn.commit()
    conn.close()


# Notification Log

def has_been_notified(user_id: int, tmdb_id: int, media_type: str, event_type: str) -> bool:
    conn = get_connection()
    row = conn.execute("""
        SELECT 1 FROM notification_log
        WHERE user_id = ? AND tmdb_id = ? AND media_type = ? AND event_type = ?
    """, (user_id, tmdb_id, media_type, event_type)).fetchone()
    conn.close()
    return row is not None


def log_notification(user_id: int, tmdb_id: int, media_type: str, event_type: str):
    conn = get_connection()
    conn.execute("""
        INSERT OR IGNORE INTO notification_log (user_id, tmdb_id, media_type, event_type)
        VALUES (?, ?, ?, ?)
    """, (user_id, tmdb_id, media_type, event_type))
    conn.commit()
    conn.close()