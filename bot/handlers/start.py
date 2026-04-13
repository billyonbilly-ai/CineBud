# bot/handlers/start.py
from telegram import Update
from telegram.ext import ContextTypes
from db import queries
from bot.keyboards import genre_keyboard


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    queries.upsert_user(user.id, user.username, user.first_name)

    # Check if user already has genres set
    existing_genres = queries.get_user_genres(user.id)

    if existing_genres:
        genre_names = ", ".join(g["genre_name"] for g in existing_genres)
        await update.message.reply_text(
            f"Welcome back! 🎬 You're already set up with: {genre_names}.\n\n"
            f"Use /mysubs to manage your tracked titles or /search to add more."
        )
        return

    await update.message.reply_text(
        f"Hey {user.first_name}! I'm CineBud 🎬\n\n"
        f"I keep you in the loop on news, trailers, new releases, and episode drops "
        f"for the kinds of films and shows you're into.\n\n"
        f"First things first, pick the genres you're into. "
        f"You can select as many as you want:",
        reply_markup=genre_keyboard()
    )