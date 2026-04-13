from telegram import Update
from telegram.ext import ContextTypes
from db import queries
from bot.keyboards import genre_keyboard, confirm_keyboard


# Temporary store for pending genre selections per user
pending_genres: dict[int, list[int]] = {}


async def handle_genre_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "genres_done":
        selected = pending_genres.get(user_id, [])

        if not selected:
            await query.edit_message_text(
                "You haven't selected any genres yet! Pick at least one."
            )
            await query.edit_message_reply_markup(genre_keyboard())
            return

        # Map selected IDs to full genre dicts and save
        from tmdb.client import GENRES
        genres_to_save = [g for g in GENRES if g["genre_id"] in selected]
        queries.save_user_genres(user_id, genres_to_save)
        pending_genres.pop(user_id, None)

        await query.edit_message_text(
            "Sorted! I'll keep you posted on anything worth knowing 🍿\n\n"
            "Want to track any specific titles too? "
            "I'll make sure you never miss a thing on those.",
            reply_markup=confirm_keyboard()
        )
        return

    # Toggle genre selection
    genre_id = int(data.replace("genre_", ""))
    selected = pending_genres.get(user_id, [])

    if genre_id in selected:
        selected.remove(genre_id)
    else:
        selected.append(genre_id)

    pending_genres[user_id] = selected

    await query.edit_message_reply_markup(genre_keyboard(selected))


async def handle_track_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "track_yes":
        await query.edit_message_text(
            "Use /search followed by a title to find it.\n\nExample: /search Sinners"
        )
    elif query.data == "track_no":
        await query.edit_message_text(
            "All good! I'll start watching out for anything in your genres 🎬"
        )


async def handle_track_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "track_cancel":
        await query.edit_message_text("Search cancelled.")
        return

    _, tmdb_id, media_type = query.data.split("_", 2)
    tmdb_id = int(tmdb_id)

    # Get title name from TMDB details
    from tmdb.client import get_movie_details, get_tv_details
    if media_type == "movie":
        details = await get_movie_details(tmdb_id)
        title = details.get("title", "Unknown")
    else:
        details = await get_tv_details(tmdb_id)
        title = details.get("name", "Unknown")

    queries.add_user_title(user_id, tmdb_id, media_type, title)

    await query.edit_message_text(
        f"Locked in! I'll hit you up the moment anything drops for {title} 🎬"
    )