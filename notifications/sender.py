from telegram import Bot
from telegram.error import Forbidden
from db import queries

async def send_notification(bot: Bot, user_id: int, message: str):
    """Send a notification to a user, clean up if they've blocked the bot."""
    try:
        await bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="HTML"
        )
    except Forbidden:
        # User blocked the bot, remove all their data
        _remove_blocked_user(user_id)


def _remove_blocked_user(user_id: int):
    conn = queries.get_connection()
    conn.execute("DELETE FROM user_genres WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM user_titles WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM notification_log WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


async def broadcast(bot: Bot, user_ids: list[int], message: str):
    """Send the same message to multiple users."""
    for user_id in user_ids:
        await send_notification(bot, user_id, message)