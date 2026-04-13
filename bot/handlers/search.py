from telegram import Update
from telegram.ext import ContextTypes
from tmdb.client import search_titles
from bot.keyboards import search_result_keyboard


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "What are you looking for? Use it like this:\n/search Avengers"
        )
        return

    query = " ".join(context.args)
    results = await search_titles(query)

    if not results:
        await update.message.reply_text(
            f"Couldn't find anything for '{query}'. Try a different title."
        )
        return

    await update.message.reply_text(
        f"Here's what I found for '{query}' — tap to track it:",
        reply_markup=search_result_keyboard(results)
    )