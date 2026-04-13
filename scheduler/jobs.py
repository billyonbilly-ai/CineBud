import logging
from db import queries
from tmdb.client import get_movie_details, get_tv_details, discover_by_genre, GENRES
from notifications.sender import send_notification
from notifications.gemini import craft_notification_safe

logger = logging.getLogger(__name__)


def _extract_state(details: dict, media_type: str) -> dict:
    """Pull out the fields we care about tracking for changes."""
    if media_type == "movie":
        videos = details.get("videos", {}).get("results", [])
        trailers = [v for v in videos if v.get("type") == "Trailer"]
        return {
            "status": details.get("status"),
            "release_date": details.get("release_date"),
            "trailer_count": len(trailers),
            "latest_trailer_key": trailers[0].get("key") if trailers else None
        }
    else:
        videos = details.get("videos", {}).get("results", [])
        trailers = [v for v in videos if v.get("type") == "Trailer"]
        return {
            "status": details.get("status"),
            "last_episode": details.get("last_episode_to_air", {}).get("id") if details.get("last_episode_to_air") else None,
            "next_episode_date": details.get("next_episode_to_air", {}).get("air_date") if details.get("next_episode_to_air") else None,
            "trailer_count": len(trailers),
            "latest_trailer_key": trailers[0].get("key") if trailers else None
        }


def _detect_changes(old: dict, new: dict, media_type: str) -> list[dict]:
    """Compare old and new state, return list of detected events."""
    events = []

    if old.get("trailer_count", 0) < new.get("trailer_count", 0):
        events.append({
            "event_type": "trailer",
            "detail": "A new trailer just dropped"
        })

    if media_type == "movie":
        if not old.get("release_date") and new.get("release_date"):
            events.append({
                "event_type": "release_date",
                "detail": f"Release date confirmed: {new['release_date']}"
            })
        if old.get("status") != new.get("status") and new.get("status") == "Released":
            events.append({
                "event_type": "released",
                "detail": "The film is now out!"
            })
    else:
        if old.get("last_episode") != new.get("last_episode") and new.get("last_episode"):
            events.append({
                "event_type": "new_episode",
                "detail": "A new episode just aired"
            })
        if old.get("status") != new.get("status"):
            events.append({
                "event_type": "status_change",
                "detail": f"Show status changed to: {new['status']}"
            })

    return events


async def _process_title(bot, tmdb_id: int, media_type: str, title: str, user_ids: list[int]):
    try:
        if media_type == "movie":
            details = await get_movie_details(tmdb_id)
        else:
            details = await get_tv_details(tmdb_id)

        new_state = _extract_state(details, media_type)
        old_state = queries.get_title_state(tmdb_id, media_type)

        if old_state is None:
            # First time seeing this title — just save state, don't notify
            queries.set_title_state(tmdb_id, media_type, new_state)
            return

        events = _detect_changes(old_state, new_state, media_type)

        for event in events:
            for user_id in user_ids:
                if queries.has_been_notified(user_id, tmdb_id, media_type, event["event_type"]):
                    continue

                # Get user's first name for Gemini
                conn = queries.get_connection()
                row = conn.execute(
                    "SELECT first_name FROM users WHERE user_id = ?", (user_id,)
                ).fetchone()
                conn.close()
                first_name = row["first_name"] if row else "there"

                raw_info = {
                    "title": title,
                    "media_type": media_type,
                    "event_type": event["event_type"],
                    "detail": event["detail"]
                }

                message = await craft_notification_safe(raw_info, first_name)
                await send_notification(bot, user_id, message)
                queries.log_notification(user_id, tmdb_id, media_type, event["event_type"])

        queries.set_title_state(tmdb_id, media_type, new_state)

    except Exception as e:
        logger.error(f"Error processing title {title} ({tmdb_id}): {e}")


async def poll_tmdb(bot):
    logger.info("Running TMDB poll...")

    # 1. Poll specifically tracked titles
    tracked = queries.get_all_tracked_titles()
    for item in tracked:
        user_ids = queries.get_users_tracking_title(item["tmdb_id"], item["media_type"])
        if user_ids:
            await _process_title(bot, item["tmdb_id"], item["media_type"], item["title"], user_ids)

    # 2. Poll by genre — discover popular titles matching user genres
    all_genre_ids = set()
    all_user_ids = queries.get_all_user_ids()

    for user_id in all_user_ids:
        genres = queries.get_user_genres(user_id)
        for g in genres:
            all_genre_ids.add(g["genre_id"])

    for genre_id in all_genre_ids:
        genre = next((g for g in GENRES if g["genre_id"] == genre_id), None)
        if not genre:
            continue

        for media_type in ("movie", "tv"):
            try:
                results = await discover_by_genre(genre_id, media_type)
                # Take top 5 most popular per genre to keep API calls manageable
                for item in results[:5]:
                    tmdb_id = item["id"]
                    title = item.get("title") or item.get("name", "Unknown")
                    user_ids = queries.get_all_users_with_genre(genre_id)
                    await _process_title(bot, tmdb_id, media_type, title, user_ids)
            except Exception as e:
                logger.error(f"Error discovering genre {genre_id} ({media_type}): {e}")

    logger.info("TMDB poll complete.")