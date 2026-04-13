import logging
from telegram import BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler
)
from config import BOT_TOKEN
from db.database import init_db
from scheduler.runner import start_scheduler, stop_scheduler
from bot.handlers.start import start
from bot.handlers.search import search
from bot.handlers.mysubs import mysubs, handle_remove_title
from bot.handlers.subscribe import (
    handle_genre_callback,
    handle_track_confirm,
    handle_track_selection
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def post_init(application):
    """Runs after the bot starts — set commands and start scheduler."""
    await application.bot.set_my_commands([
        BotCommand("start", "Set up your preferences"),
        BotCommand("search", "Search for a specific title to track"),
        BotCommand("mysubs", "View and manage your tracked titles"),
    ])

    init_db()
    start_scheduler(application.bot)
    logger.info("CineBud is live.")


async def post_shutdown(application):
    stop_scheduler()
    logger.info("CineBud shut down.")


def main():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("mysubs", mysubs))

    # Callback query handlers
    app.add_handler(CallbackQueryHandler(handle_genre_callback, pattern="^genre_|^genres_done$"))
    app.add_handler(CallbackQueryHandler(handle_track_confirm, pattern="^track_yes$|^track_no$"))
    app.add_handler(CallbackQueryHandler(handle_track_selection, pattern="^track_|^track_cancel$"))
    app.add_handler(CallbackQueryHandler(handle_remove_title, pattern="^remove_|^subs_done$"))

    logger.info("Starting CineBud...")
    app.run_polling()


if __name__ == "__main__":
    main()