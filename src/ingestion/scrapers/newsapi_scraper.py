"""
NewsAPI Scraper
Fetches latest news articles from newsapi.org
Sign up for a free key at: https://newsapi.org/register
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict
from config.settings import NEWSAPI_KEY, NEWSAPI_QUERY, NEWSAPI_PAGE_SIZE


def fetch_news(query: str = NEWSAPI_QUERY, page_size: int = NEWSAPI_PAGE_SIZE) -> List[Dict]:
    """
    Fetch news articles from NewsAPI.

    Returns a list of normalized article dicts:
        {source, title, content, url, published_at}
    """
    if not NEWSAPI_KEY:
        raise ValueError("NEWSAPI_KEY is not set in your .env file")

    from_date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": from_date,
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "language": "en",
        "apiKey": NEWSAPI_KEY,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    articles = []
    for item in data.get("articles", []):
        # Skip articles with no content
        if not item.get("content") and not item.get("description"):
            continue

        articles.append({
            "source": "newsapi",
            "title": item.get("title", ""),
            "content": item.get("content") or item.get("description", ""),
            "url": item.get("url", ""),
            "published_at": item.get("publishedAt", ""),
        })

    print(f"[NewsAPI] Fetched {len(articles)} articles")
    return articles


if __name__ == "__main__":
    articles = fetch_news()
    for a in articles[:3]:
        print(f"- {a['title']}")
