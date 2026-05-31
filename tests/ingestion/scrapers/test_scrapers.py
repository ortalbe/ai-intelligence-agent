"""
Tests for the scrapers module.

We use unittest.mock to fake HTTP responses so tests:
  - Don't hit the real internet (fast + reliable)
  - Work without API keys
  - Test our parsing logic in isolation

Key concept: patch replaces a real function with a fake one during the test.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime


# ─────────────────────────────────────────────
# Helpers — fake API responses
# ─────────────────────────────────────────────

def make_mock_response(json_data=None, text_data=None, status_code=200):
    """Creates a fake requests.Response object."""
    mock = MagicMock()
    mock.status_code = status_code
    if json_data is not None:
        mock.json.return_value = json_data
    if text_data is not None:
        mock.text = text_data
    mock.raise_for_status = MagicMock()  # does nothing (no error)
    return mock


FAKE_NEWSAPI_RESPONSE = {
    "status": "ok",
    "articles": [
        {
            "title": "AI Breakthrough in 2026",
            "content": "Researchers have developed a new model...",
            "description": "A major step forward in AI research.",
            "url": "https://example.com/article1",
            "publishedAt": "2026-05-31T10:00:00Z",
        },
        {
            "title": "No Content Article",
            "content": None,
            "description": None,  # should be skipped
            "url": "https://example.com/article2",
            "publishedAt": "2026-05-31T09:00:00Z",
        },
    ],
}

FAKE_HN_TOP_STORIES = [1001, 1002, 1003]

FAKE_HN_STORY = {
    "id": 1001,
    "type": "story",
    "title": "Show HN: My AI Project",
    "url": "https://example.com/hn-story",
    "text": None,
    "time": 1748649600,
}

FAKE_ARXIV_XML = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>https://arxiv.org/abs/2601.00001</id>
    <title>Advances in Large Language Models</title>
    <summary>This paper presents new findings in LLMs...</summary>
    <published>2026-01-01T00:00:00Z</published>
  </entry>
  <entry>
    <id>https://arxiv.org/abs/2601.00002</id>
    <title>RAG Systems at Scale</title>
    <summary>We explore retrieval-augmented generation...</summary>
    <published>2026-01-02T00:00:00Z</published>
  </entry>
  <entry>
    <id>https://arxiv.org/abs/2601.00003</id>
    <title>Empty Abstract Paper</title>
    <summary></summary>  <!-- should be skipped -->
    <published>2026-01-03T00:00:00Z</published>
  </entry>
</feed>"""


# ─────────────────────────────────────────────
# NewsAPI Tests
# ─────────────────────────────────────────────

class TestNewsAPIScraper(unittest.TestCase):

    @patch("src.ingestion.scrapers.newsapi_scraper.NEWSAPI_KEY", "fake-key-123")
    @patch("src.ingestion.scrapers.newsapi_scraper.requests.get")
    def test_returns_list_of_articles(self, mock_get):
        """fetch_news should return a list of normalized article dicts."""
        mock_get.return_value = make_mock_response(json_data=FAKE_NEWSAPI_RESPONSE)

        from src.ingestion.scrapers.newsapi_scraper import fetch_news
        articles = fetch_news()

        self.assertIsInstance(articles, list)

    @patch("src.ingestion.scrapers.newsapi_scraper.NEWSAPI_KEY", "fake-key-123")
    @patch("src.ingestion.scrapers.newsapi_scraper.requests.get")
    def test_skips_articles_with_no_content(self, mock_get):
        """Articles with no content AND no description should be skipped."""
        mock_get.return_value = make_mock_response(json_data=FAKE_NEWSAPI_RESPONSE)

        from src.ingestion.scrapers.newsapi_scraper import fetch_news
        articles = fetch_news()

        # Only 1 of 2 articles has content — the second should be skipped
        self.assertEqual(len(articles), 1)

    @patch("src.ingestion.scrapers.newsapi_scraper.NEWSAPI_KEY", "fake-key-123")
    @patch("src.ingestion.scrapers.newsapi_scraper.requests.get")
    def test_article_has_required_fields(self, mock_get):
        """Each article must have: source, title, content, url, published_at."""
        mock_get.return_value = make_mock_response(json_data=FAKE_NEWSAPI_RESPONSE)

        from src.ingestion.scrapers.newsapi_scraper import fetch_news
        articles = fetch_news()

        required_fields = {"source", "title", "content", "url", "published_at"}
        for article in articles:
            self.assertTrue(required_fields.issubset(article.keys()))

    @patch("src.ingestion.scrapers.newsapi_scraper.NEWSAPI_KEY", "fake-key-123")
    @patch("src.ingestion.scrapers.newsapi_scraper.requests.get")
    def test_source_field_is_newsapi(self, mock_get):
        """source field should always be 'newsapi'."""
        mock_get.return_value = make_mock_response(json_data=FAKE_NEWSAPI_RESPONSE)

        from src.ingestion.scrapers.newsapi_scraper import fetch_news
        articles = fetch_news()

        for article in articles:
            self.assertEqual(article["source"], "newsapi")

    @patch("src.ingestion.scrapers.newsapi_scraper.NEWSAPI_KEY", "")
    def test_raises_error_when_no_api_key(self):
        """fetch_news should raise ValueError if NEWSAPI_KEY is not set."""
        from src.ingestion.scrapers.newsapi_scraper import fetch_news

        with self.assertRaises(ValueError) as ctx:
            fetch_news()

        self.assertIn("NEWSAPI_KEY", str(ctx.exception))

    @patch("src.ingestion.scrapers.newsapi_scraper.NEWSAPI_KEY", "fake-key-123")
    @patch("src.ingestion.scrapers.newsapi_scraper.requests.get")
    def test_empty_articles_list(self, mock_get):
        """fetch_news should return empty list if API returns no articles."""
        mock_get.return_value = make_mock_response(json_data={"status": "ok", "articles": []})

        from src.ingestion.scrapers.newsapi_scraper import fetch_news
        articles = fetch_news()

        self.assertEqual(articles, [])


# ─────────────────────────────────────────────
# HackerNews Tests
# ─────────────────────────────────────────────

class TestHackerNewsScraper(unittest.TestCase):

    @patch("src.ingestion.scrapers.hackernews_scraper.requests.get")
    def test_returns_list_of_stories(self, mock_get):
        """fetch_hackernews should return a list of story dicts."""
        mock_get.side_effect = [
            make_mock_response(json_data=FAKE_HN_TOP_STORIES),  # top stories call
            make_mock_response(json_data=FAKE_HN_STORY),        # story 1001
            make_mock_response(json_data={**FAKE_HN_STORY, "id": 1002}),
            make_mock_response(json_data={**FAKE_HN_STORY, "id": 1003}),
        ]

        from src.ingestion.scrapers.hackernews_scraper import fetch_hackernews
        stories = fetch_hackernews(limit=3)

        self.assertIsInstance(stories, list)
        self.assertGreater(len(stories), 0)

    @patch("src.ingestion.scrapers.hackernews_scraper.requests.get")
    def test_story_has_required_fields(self, mock_get):
        """Each story must have: source, title, content, url, published_at."""
        mock_get.side_effect = [
            make_mock_response(json_data=[1001]),
            make_mock_response(json_data=FAKE_HN_STORY),
        ]

        from src.ingestion.scrapers.hackernews_scraper import fetch_hackernews
        stories = fetch_hackernews(limit=1)

        required_fields = {"source", "title", "content", "url", "published_at"}
        for story in stories:
            self.assertTrue(required_fields.issubset(story.keys()))

    @patch("src.ingestion.scrapers.hackernews_scraper.requests.get")
    def test_source_field_is_hackernews(self, mock_get):
        """source field should always be 'hackernews'."""
        mock_get.side_effect = [
            make_mock_response(json_data=[1001]),
            make_mock_response(json_data=FAKE_HN_STORY),
        ]

        from src.ingestion.scrapers.hackernews_scraper import fetch_hackernews
        stories = fetch_hackernews(limit=1)

        for story in stories:
            self.assertEqual(story["source"], "hackernews")

    @patch("src.ingestion.scrapers.hackernews_scraper.requests.get")
    def test_skips_non_story_types(self, mock_get):
        """Items that are not type 'story' (e.g. comments, jobs) should be skipped."""
        job_item = {**FAKE_HN_STORY, "type": "job"}
        mock_get.side_effect = [
            make_mock_response(json_data=[1001]),
            make_mock_response(json_data=job_item),
        ]

        from src.ingestion.scrapers.hackernews_scraper import fetch_hackernews
        stories = fetch_hackernews(limit=1)

        self.assertEqual(stories, [])


# ─────────────────────────────────────────────
# ArXiv Tests
# ─────────────────────────────────────────────

class TestArXivScraper(unittest.TestCase):

    @patch("src.ingestion.scrapers.arxiv_scraper.requests.get")
    def test_returns_list_of_papers(self, mock_get):
        """fetch_arxiv should return a list of paper dicts."""
        mock_get.return_value = make_mock_response(text_data=FAKE_ARXIV_XML)

        from src.ingestion.scrapers.arxiv_scraper import fetch_arxiv
        papers = fetch_arxiv()

        self.assertIsInstance(papers, list)
        self.assertGreater(len(papers), 0)

    @patch("src.ingestion.scrapers.arxiv_scraper.requests.get")
    def test_skips_papers_with_empty_abstract(self, mock_get):
        """Papers with empty abstract should be skipped."""
        mock_get.return_value = make_mock_response(text_data=FAKE_ARXIV_XML)

        from src.ingestion.scrapers.arxiv_scraper import fetch_arxiv
        papers = fetch_arxiv()

        # 3 entries in XML but 1 has empty abstract — expect 2
        self.assertEqual(len(papers), 2)

    @patch("src.ingestion.scrapers.arxiv_scraper.requests.get")
    def test_paper_has_required_fields(self, mock_get):
        """Each paper must have: source, title, content, url, published_at."""
        mock_get.return_value = make_mock_response(text_data=FAKE_ARXIV_XML)

        from src.ingestion.scrapers.arxiv_scraper import fetch_arxiv
        papers = fetch_arxiv()

        required_fields = {"source", "title", "content", "url", "published_at"}
        for paper in papers:
            self.assertTrue(required_fields.issubset(paper.keys()))

    @patch("src.ingestion.scrapers.arxiv_scraper.requests.get")
    def test_source_field_is_arxiv(self, mock_get):
        """source field should always be 'arxiv'."""
        mock_get.return_value = make_mock_response(text_data=FAKE_ARXIV_XML)

        from src.ingestion.scrapers.arxiv_scraper import fetch_arxiv
        papers = fetch_arxiv()

        for paper in papers:
            self.assertEqual(paper["source"], "arxiv")

    @patch("src.ingestion.scrapers.arxiv_scraper.requests.get")
    def test_content_includes_title_and_abstract(self, mock_get):
        """content field should combine title + abstract."""
        mock_get.return_value = make_mock_response(text_data=FAKE_ARXIV_XML)

        from src.ingestion.scrapers.arxiv_scraper import fetch_arxiv
        papers = fetch_arxiv()

        first = papers[0]
        self.assertIn(first["title"], first["content"])


# ─────────────────────────────────────────────
# Run all tests
# ─────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
