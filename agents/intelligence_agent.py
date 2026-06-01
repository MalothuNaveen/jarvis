# ============================================================
#  agents/intelligence_agent.py  — Agent 8: Real-World Intelligence Agent 🌍
#  News, GitHub trends, weather — free APIs, zero cost
# ============================================================

import asyncio
import httpx
import feedparser
from .base import BaseAgent
from rich.console import Console

console = Console()

# ── Free data sources ─────────────────────────────────────────
GITHUB_TRENDING_URL = "https://github.com/trending"
RSS_FEEDS = {
    "tech"   : "https://feeds.feedburner.com/TechCrunch",
    "ai"     : "https://www.artificialintelligence-news.com/feed/",
    "hacker" : "https://hnrss.org/frontpage",
}
WEATHER_URL = "https://wttr.in/{city}?format=3"   # free, no API key


class IntelligenceAgent(BaseAgent):
    agent_id = "intelligence"

    async def execute(self, intent: str, params: dict, raw: str) -> str:
        intent_lower = intent.lower()

        if "weather" in intent_lower:
            city = params.get("city", "London")
            return await self._get_weather(city)

        if any(k in intent_lower for k in ["github", "trending", "open source"]):
            return await self._github_trending()

        if any(k in intent_lower for k in ["news", "headlines", "update"]):
            topic = params.get("topic", "tech")
            return await self._get_news(topic)

        # Default: return a combined digest
        return await self._digest()

    # ── Weather ──────────────────────────────────────────────
    async def _get_weather(self, city: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(WEATHER_URL.format(city=city))
                if r.status_code == 200:
                    return f"Weather — {r.text.strip()}"
                return f"Could not fetch weather for {city}."
        except Exception as e:
            return f"Weather fetch error: {e}"

    # ── GitHub Trending (scrape, no API key) ─────────────────
    async def _github_trending(self) -> str:
        try:
            from bs4 import BeautifulSoup
            async with httpx.AsyncClient(timeout=15, follow_redirects=True,
                                          headers={"User-Agent": "Mozilla/5.0"}) as client:
                r = await client.get(GITHUB_TRENDING_URL)
                soup  = BeautifulSoup(r.text, "html.parser")
                repos = soup.select("article.Box-row h2 a")[:5]
                names = [r.get_text(strip=True).replace("\n","").replace(" ","") for r in repos]
                return "GitHub Trending today: " + " | ".join(names)
        except Exception as e:
            return f"GitHub trending error: {e}"

    # ── RSS News ─────────────────────────────────────────────
    async def _get_news(self, topic: str = "tech") -> str:
        url = RSS_FEEDS.get(topic.lower(), RSS_FEEDS["tech"])
        try:
            feed     = feedparser.parse(url)
            entries  = feed.entries[:5]
            headlines = [e.title for e in entries]
            return f"Top {topic} headlines: " + " | ".join(headlines)
        except Exception as e:
            return f"News fetch error: {e}"

    # ── Combined morning digest ───────────────────────────────
    async def _digest(self) -> str:
        weather, news = await asyncio.gather(
            self._get_weather("London"),
            self._get_news("tech"),
        )
        return f"{weather}. {news}"
