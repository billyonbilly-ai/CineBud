import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Optional: override the default Groq API URL if needed
GROQ_URL = os.getenv("GROQ_URL", "https://api.groq.ai/v1/generate")