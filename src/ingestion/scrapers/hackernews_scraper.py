"""
Hacker News Scraper
Uses the official HN Firebase API (no key required).
Fetches top stories with their full text.
"""

import requests
from typing import List, Dict
from config.settings import HACKERNEWS_LIMIT

HN_BASE = "https://hacker-news.firebaseio.com/v0"


def fetch_top_story_ids(limit: int = HACKERNEWS_LIMIT) -> List[int]:
    response = requests.get(f"{HN_BASE}/topstories.json", timeout=10)
    response.raise_for_status()
    return response.json()[:limit]


def fetch_story(story_id: int) -> Dict | None:
    response = requests.get(f"{HN_BASE}/item/{story_id}.json", timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_hackernews(limit: int = HACKERNEWS_LIMIT) -> List[Dict]:
    """
    Fetch top stories from Hacker News.

    Returns a list of normalized dicts:
        {source, title, content, url, published_at}
    """
    story_ids = fetch_top_story_ids(limit)

    articles = []
    for story_id in story_ids:
        story = fetch_story(story_id)
        if not story or story.get("type") != "story":
            continue

        # HN stories often have a URL but no body text - use title as content fallback
        content = story.get("text") or story.get("title", "")

        articles.append({
            "source": "hackernews",
            "title": story.get("title", ""),
            "content": content,
            "url": story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
            "published_at": str(story.get("time", "")),
        })

    print(f"[HackerNews] Fetched {len(articles)} stories")
    return articles


if __name__ == "__main__":
    stories = fetch_hackernews()
    for s in stories[:3]:
        print(f"- {s['title']}")
