# CineBud: Your Enthusiastic Cinema Buddy

**CineBud** is a Telegram bot designed for film and TV buffs who want to stay ahead of the curve. It tracks movie and TV news via the TMDB API and uses Google’s Gemini AI to deliver updates with the energy and personality of a friend who lives and breathes cinema.

---

## What It Does

- **Genre Tracking:** On first launch, users select their favorite genres. CineBud keeps them updated on broad news within those categories.
- **Specific Title Tracking:** Users can opt to track specific movies or TV shows for precise updates.
- **AI-Powered Notifications:** Instead of robotic alerts, CineBud uses Gemini 2.0 Flash to rewrite raw TMDB data into enthusiastic, friendly messages.
- **Smart Updates:** Monitors for trailers, new episodes, release dates, and status changes.

---

## Tech Stack

- **Language:** Python 3.10+
- **Bot Framework:** `python-telegram-bot`
- **AI Engine:** Google Gemini 3.0 Flash
- **Data Source:** TMDB (The Movie Database) API
- **Database:** SQLite (local persistence)
- **HTTP Client:** `httpx` (Asynchronous requests)

---

## Setup & Installation

### 1. Prerequisites

You will need to obtain the following keys:

- **Telegram Bot Token:** Create a bot via [@BotFather](https://t.me/botfather).
- **TMDB API Key:** Register at [themoviedb.org](https://www.themoviedb.org/documentation/api).
- **Gemini API Key:** Obtain one from [Google AI Studio](https://aistudio.google.com/).

### 2. Local Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/billyonbilly-ai/CineBud.git
    cd cinebud
    ```
2.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    # OR
    venv\Scripts\activate     # Windows
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure Environment Variables:**
    Create a `.env` file in the root directory:
    ```env
    BOT_TOKEN=your_telegram_bot_token
    TMDB_API_KEY=your_tmdb_api_key
    GEMINI_API_KEY=your_gemini_api_key
    ```

---

## Deployment (Hosting)

This project is optimized for deployment on platforms like **JustRunMy.App**.

### Step 1: Prepare the Archive

To ensure a clean deployment without local junk, use `tar` to create your zip. Run this in your project root to create an archive.zip file:

```bash
tar -a -c --exclude='*__pycache__*' --exclude='venv' --exclude='cinebud.db' -f archive.zip bot db notifications scheduler tmdb config.py Dockerfile requirements.txt
```

### Step 2: Upload archive.zip to JustRunMy.App

1.  **Create new application:** Sign in, create a new application then upload files using the **Upload Archive** button.
2.  **Environment Variables:** You will be prompted to add your `BOT_TOKEN`, `TMDB_API_KEY`, and `GEMINI_API_KEY`.
3.  **Run Command:** Under settings, set the command to:
    ```bash
    python -m bot.main
    ```
4.  **Persistence:** Under settings add a **Volume Mapping** to `/app` to ensure the `cinebud.db` SQLite file is not lost when the bot restarts.

---

## Project Structure

```text
cinebud/
├── bot/              # Core bot logic and handlers
├── db/               # SQLite database schemas and connection logic
├── notifications/    # Gemini AI notification crafting
├── scheduler/        # Background tasks for checking TMDB updates
├── tmdb/             # API wrappers for movie/TV data
├── cinebud.db        # Local SQLite database (auto-generated)
├── config.py         # Configuration and env loading
└── requirements.txt  # Project dependencies
```

---

## How the AI Works

CineBud uses a specialized `SYSTEM_PROMPT` to maintain its personality. It takes raw event data (e.g., "Trailer dropped") and transforms it into:

> _"Hey Billy! You won't believe it, but the first official trailer for Avengers: Doomsday just dropped! 🎬 I'm so hyped, you have to see this!"_

![photo_2026-04-14_12-47-34](https://github.com/user-attachments/assets/0f41de0e-ae7d-4ecf-98bb-8996024eb978)
