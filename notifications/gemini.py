import httpx
from config import GEMINI_API_KEY

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent"

SYSTEM_PROMPT = """You are CineBud, an enthusiastic cinema lover who keeps friends updated on film and TV news. 
Your job is to take raw film/TV update info and rewrite it as a short, exciting notification message.

Rules:
- Always sound genuinely excited and passionate about cinema — this is your thing
- Keep it short: 3-5 sentences max
- You are given the user's first name. Use it occasionally and naturally — not in every message. 
  Sometimes just dive straight into the news. Vary it like a real person would.
- Never sound corporate or robotic
- Use 1-2 relevant emojis max, don't overdo it
- Never use hashtags
- Speak like a friend who just found out something exciting and had to tell you immediately
- The excitement should always be there, with or without the name
"""

async def craft_notification(raw_info: dict, first_name: str) -> str:
    """
    raw_info: {
        "title": "Avengers: Doomsday",
        "media_type": "movie",
        "event_type": "trailer",  # trailer | release_date | new_episode | status_change
        "detail": "First official trailer just dropped"
    }
    """
    prompt = f"""
User's first name: {first_name}

Film/TV update to announce:
- Title: {raw_info['title']}
- Type: {raw_info['media_type']}
- Event: {raw_info['event_type']}
- Detail: {raw_info['detail']}

Write the notification message now.
"""

    payload = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": [
            {"parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "temperature": 0.9,
            "maxOutputTokens": 200
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            GEMINI_URL,
            headers={"Content-Type": "application/json"},
            params={"key": GEMINI_API_KEY},
            json=payload,
            timeout=15.0
        )
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()


async def craft_notification_safe(raw_info: dict, first_name: str) -> str:
    """Fallback to a plain message if Gemini fails."""
    try:
        return await craft_notification(raw_info, first_name)
    except Exception:
        # Plain fallback that is still readable
        return (
            f"🎬 <b>{raw_info['title']}</b>\n"
            f"{raw_info['detail']}"
        )