"""
Tests for the scrapers module - nes API.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

# ─────────────────────────────────────────────
# NewsAPI Tests
# ─────────────────────────────────────────────

class TestNewsAPIScraperReal (unittest.TestCase):

    def test_returns_list_of_real_articles_from_news_api(self):
        """fetch real news should return a list of normalized article dicts."""

        from src.ingestion.scrapers.newsapi_scraper import fetch_news
        articles = fetch_news()

        self.assertIsInstance(articles, list)
        if articles:
            self.assertIn("title", articles[0])
            self.assertIn("source", articles[0])
            self.assertEqual(articles[0]["source"], "newsapi")

