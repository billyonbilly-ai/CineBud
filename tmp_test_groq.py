import asyncio
from notifications.groq import craft_notification_safe


async def t():
    raw = {
        "title": "Test Movie",
        "media_type": "movie",
        "event_type": "trailer",
        "detail": "A test trailer just dropped"
    }
    print(await craft_notification_safe(raw, "Alex"))


if __name__ == '__main__':
    asyncio.run(t())
