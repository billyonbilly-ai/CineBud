import httpx
from config import TMDB_API_KEY

BASE_URL = "https://api.themoviedb.org/3"
HEADERS = {
    "Authorization": f"Bearer {TMDB_API_KEY}",
    "accept": "application/json"
}


GENRES = [
    {"genre_id": 28,    "genre_name": "Action"},
    {"genre_id": 10759, "genre_name": "Action & Adventure"},
    {"genre_id": 12,    "genre_name": "Adventure"},
    {"genre_id": 16,    "genre_name": "Animation"},
    {"genre_id": 35,    "genre_name": "Comedy"},
    {"genre_id": 80,    "genre_name": "Crime"},
    {"genre_id": 99,    "genre_name": "Documentary"},
    {"genre_id": 18,    "genre_name": "Drama"},
    {"genre_id": 14,    "genre_name": "Fantasy"},
    {"genre_id": 27,    "genre_name": "Horror"},
    {"genre_id": 9648,  "genre_name": "Mystery"},
    {"genre_id": 10749, "genre_name": "Romance"},
    {"genre_id": 878,   "genre_name": "Sci-Fi"},
    {"genre_id": 10765, "genre_name": "Sci-Fi & Fantasy"},
    {"genre_id": 53,    "genre_name": "Thriller"},
    {"genre_id": 10752, "genre_name": "War"},
    {"genre_id": 37,    "genre_name": "Western"},
    {"genre_id": 10764, "genre_name": "Reality"},
]


async def search_titles(query: str) -> list[dict]:
    """Search for movies and TV shows by name."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/search/multi",
            headers=HEADERS,
            params={"query": query, "include_adult": False}
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        return [
            r for r in results
            if r.get("media_type") in ("movie", "tv")
        ]


async def get_movie_details(tmdb_id: int) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/movie/{tmdb_id}",
            headers=HEADERS,
            params={"append_to_response": "videos"}
        )
        response.raise_for_status()
        return response.json()


async def get_tv_details(tmdb_id: int) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/tv/{tmdb_id}",
            headers=HEADERS,
            params={"append_to_response": "videos"}
        )
        response.raise_for_status()
        return response.json()


async def discover_by_genre(genre_id: int, media_type: str) -> list[dict]:
    """Fetch recent/upcoming titles for a given genre."""
    endpoint = "movie" if media_type == "movie" else "tv"
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/discover/{endpoint}",
            headers=HEADERS,
            params={
                "with_genres": genre_id,
                "sort_by": "popularity.desc",
                "page": 1
            }
        )
        response.raise_for_status()
        return response.json().get("results", [])


async def get_upcoming_movies() -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/movie/upcoming",
            headers=HEADERS,
            params={"page": 1}
        )
        response.raise_for_status()
        return response.json().get("results", [])


async def get_airing_today_tv() -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/tv/airing_today",
            headers=HEADERS,
            params={"page": 1}
        )
        response.raise_for_status()
        return response.json().get("results", [])