"""
Tests for the scrapers module - nes API.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

# ─────────────────────────────────────────────
# HackerNews Tests
# ─────────────────────────────────────────────

class TestHackerNewsScraperScraperReal (unittest.TestCase):

    def test_returns_list_of_real_articles_from_hacker_news(self):
        """fetch real news from arxiv_scraper.should return a list of normalized article dicts."""

        from src.ingestion.scrapers.hackernews_scraper import fetch_hackernews
        articles = fetch_hackernews()

        self.assertIsInstance(articles, list)
        if articles:
            self.assertIn("title", articles[0])
            self.assertIn("source", articles[0])
            self.assertEqual(articles[0]["source"], "hackernews")

