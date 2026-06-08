"""Groq-backed notification composer.

This module will prefer the official `groq` Python SDK when available and
fall back to a generic HTTP request if not. The functions expose
`craft_notification` and `craft_notification_safe`.
"""

from config import GROQ_API_KEY, GROQ_URL
import asyncio
import httpx

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


def _extract_text_from_groq_response(resp) -> str | None:
    # Try common shapes returned by the Groq SDK / API
    try:
        if isinstance(resp, dict):
            if "text" in resp and isinstance(resp["text"], str):
                return resp["text"].strip()
            if "choices" in resp and isinstance(resp["choices"], list) and resp["choices"]:
                choice = resp["choices"][0]
                if isinstance(choice, dict):
                    # streaming delta style
                    if "delta" in choice and isinstance(choice["delta"], dict) and "content" in choice["delta"]:
                        return choice["delta"]["content"].strip()
                    if "message" in choice and isinstance(choice["message"], dict) and "content" in choice["message"]:
                        return choice["message"]["content"].strip()
        # fallback: if object has attribute 'text' or str(arg)
        if hasattr(resp, "text"):
            return str(resp.text).strip()
    except Exception:
        return None
    return None


async def craft_notification(raw_info: dict, first_name: str) -> str:
    prompt = (
        f"User's first name: {first_name}\n\n"
        f"Film/TV update to announce:\n- Title: {raw_info['title']}\n- Type: {raw_info['media_type']}\n- Event: {raw_info['event_type']}\n- Detail: {raw_info['detail']}\n\n"
        "Write the notification message now."
    )

    # If the official Groq SDK is installed, prefer it.
    try:
        from groq import Groq

        client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else Groq()

        # Build chat messages: system + user
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        # The SDK may provide a streaming iterator or a completed response.
        completion = client.chat.completions.create(
            model="groq/compound",
            messages=messages,
            temperature=0.9,
            max_completion_tokens=200,
            stream=False,
        )

        # Try to extract text from known shapes
        text = _extract_text_from_groq_response(completion)
        if text:
            return text

        # As a fallback, convert to string
        return str(completion)

    except Exception:
        # SDK not installed or failed — fall back to generic HTTP request
        payload = {
            "prompt": SYSTEM_PROMPT + "\n\n" + prompt,
            "max_tokens": 200,
            "temperature": 0.9,
        }

        headers = {"Content-Type": "application/json"}
        if GROQ_API_KEY:
            headers["Authorization"] = f"Bearer {GROQ_API_KEY}"

        async with httpx.AsyncClient() as client:
            resp = await client.post(GROQ_URL, json=payload, headers=headers, timeout=15.0)
            resp.raise_for_status()
            data = resp.json()

            text = _extract_text_from_groq_response(data)
            if text:
                return text
            return str(data)


async def craft_notification_safe(raw_info: dict, first_name: str) -> str:
    try:
        return await craft_notification(raw_info, first_name)
    except Exception:
        return (
            f"🎬 <b>{raw_info['title']}</b>\n"
            f"{raw_info['detail']}"
        )
