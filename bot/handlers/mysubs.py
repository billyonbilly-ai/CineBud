from telegram import Update
from telegram.ext import ContextTypes
from db import queries
from bot.keyboards import mysubs_keyboard


async def mysubs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    titles = queries.get_user_titles(user_id)
    genres = queries.get_user_genres(user_id)

    if not titles and not genres:
        await update.message.reply_text(
            "You haven't set anything up yet. Use /start to get going."
        )
        return

    genre_names = ", ".join(g["genre_name"] for g in genres) if genres else "None"
    text = f"Your genres: {genre_names}\n\n"

    if titles:
        text += "Titles you're tracking (tap to remove):"
        await update.message.reply_text(text, reply_markup=mysubs_keyboard(titles))
    else:
        text += "You're not tracking any specific titles yet. Use /search to add some."
        await update.message.reply_text(text)


async def handle_remove_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "subs_done":
        await query.edit_message_text("All good 👍")
        return

    _, tmdb_id, media_type = query.data.split("_", 2)
    queries.remove_user_title(user_id, int(tmdb_id), media_type)

    # Refresh the list
    titles = queries.get_user_titles(user_id)
    if titles:
        await query.edit_message_reply_markup(mysubs_keyboard(titles))
    else:
        await query.edit_message_text("No more tracked titles. Use /search to add some.")