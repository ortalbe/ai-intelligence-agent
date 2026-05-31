"""
ArXiv Scraper
Uses the ArXiv public API (no key required).
Fetches latest research paper abstracts.
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict
from config.settings import ARXIV_QUERY, ARXIV_MAX_RESULTS

ARXIV_API = "http://export.arxiv.org/api/query"
NS = "{http://www.w3.org/2005/Atom}"


def fetch_arxiv(query: str = ARXIV_QUERY, max_results: int = ARXIV_MAX_RESULTS) -> List[Dict]:
    """
    Fetch recent papers from ArXiv.

    Returns a list of normalized dicts:
        {source, title, content, url, published_at}
    """
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    response = requests.get(ARXIV_API, params=params, timeout=15)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    articles = []

    for entry in root.findall(f"{NS}entry"):
        title = entry.findtext(f"{NS}title", "").strip()
        abstract = entry.findtext(f"{NS}summary", "").strip()
        url = entry.findtext(f"{NS}id", "").strip()
        published = entry.findtext(f"{NS}published", "").strip()

        if not abstract:
            continue

        articles.append({
            "source": "arxiv",
            "title": title,
            "content": f"{title}. {abstract}",
            "url": url,
            "published_at": published,
        })

    print(f"[ArXiv] Fetched {len(articles)} papers")
    return articles


if __name__ == "__main__":
    papers = fetch_arxiv()
    for p in papers[:3]:
        print(f"- {p['title']}")
