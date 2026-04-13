from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from tmdb.client import GENRES


def genre_keyboard(selected_ids: list[int] = []) -> InlineKeyboardMarkup:
    """Build genre selection keyboard. Selected genres show a checkmark."""
    buttons = []
    row = []

    for i, genre in enumerate(GENRES):
        genre_id = genre["genre_id"]
        name = genre["genre_name"]
        label = f"✅ {name}" if genre_id in selected_ids else name
        row.append(InlineKeyboardButton(label, callback_data=f"genre_{genre_id}"))

        if len(row) == 3:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append([InlineKeyboardButton("Done ✓", callback_data="genres_done")])
    return InlineKeyboardMarkup(buttons)


def confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Yes, search for titles", callback_data="track_yes"),
            InlineKeyboardButton("No, I'm good", callback_data="track_no")
        ]
    ])


def search_result_keyboard(results: list[dict]) -> InlineKeyboardMarkup:
    """Show search results as selectable buttons."""
    buttons = []
    for r in results[:5]:
        tmdb_id = r["id"]
        media_type = r.get("media_type", "movie")
        title = r.get("title") or r.get("name", "Unknown")
        year = (r.get("release_date") or r.get("first_air_date") or "")[:4]
        label = f"{title} ({year})" if year else title
        buttons.append([
            InlineKeyboardButton(label, callback_data=f"track_{tmdb_id}_{media_type}")
        ])

    buttons.append([InlineKeyboardButton("Cancel", callback_data="track_cancel")])
    return InlineKeyboardMarkup(buttons)


def mysubs_keyboard(titles: list[dict]) -> InlineKeyboardMarkup:
    """Show tracked titles with remove option."""
    buttons = []
    for t in titles:
        label = f"❌ {t['title']}"
        buttons.append([
            InlineKeyboardButton(
                label,
                callback_data=f"remove_{t['tmdb_id']}_{t['media_type']}"
            )
        ])

    if not buttons:
        return None

    buttons.append([InlineKeyboardButton("Done", callback_data="subs_done")])
    return InlineKeyboardMarkup(buttons)