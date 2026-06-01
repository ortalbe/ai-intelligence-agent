"""
Tests for the scrapers module - nes API.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

# ─────────────────────────────────────────────
# Arxiv Tests
# ─────────────────────────────────────────────

class TestArxivScraperScraperReal (unittest.TestCase):

    def test_returns_list_of_real_articles_from_arxiv(self):
        """fetch real news from arxiv_scraper.should return a list of normalized article dicts."""

        from src.ingestion.scrapers.arxiv_scraper import fetch_arxiv

        articles = fetch_arxiv()

        self.assertIsInstance(articles, list)
        if articles:
            self.assertIn("title", articles[0])
            self.assertIn("source", articles[0])
            self.assertEqual(articles[0]["source"], "arxiv")

