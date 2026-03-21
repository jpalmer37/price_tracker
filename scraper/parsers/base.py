import json
import logging
import time
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


class BaseParser(ABC):
    """Abstract base for store-specific HTML parsers.

    Use as a context manager so the browser is always shut down cleanly::

        with CostcoParser() as parser:
            info = parser.extract_info(url)
    """

    name: str | None = None

    @classmethod
    def get_name(cls) -> str | None:
        return cls.name

    def __init__(self) -> None:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(10)
        self._soup: BeautifulSoup | None = None

    # ------------------------------------------------------------------
    # Context-manager support
    # ------------------------------------------------------------------
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def close(self) -> None:
        if self.driver:
            self.driver.quit()
            logging.info(json.dumps({"event_type": "browser_closed"}))

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------
    def _get_soup(self, url: str) -> BeautifulSoup:
        """Fetch *url* and return a BeautifulSoup tree."""
        try:
            self.driver.get(url)
            time.sleep(5)
            self._soup = BeautifulSoup(self.driver.page_source, "html.parser")
        except Exception as exc:
            logging.error(json.dumps({
                "event_type": "page_fetch_failed",
                "url": url,
                "error": str(exc),
            }))
            raise ValueError(f"Could not fetch page: {url}") from exc
        return self._soup

    @staticmethod
    def _find_unique_element(soup: BeautifulSoup, tag: str, params: dict | None = None) -> str:
        params = params or {}
        elements = soup.find_all(tag, **params)
        if len(elements) > 1:
            raise ValueError(f"Found more than one matching element: {elements}")
        if len(elements) == 0:
            raise ValueError("Target element not found.")
        return str(elements[0].text).strip()

    @staticmethod
    def clean_price(price_str: str) -> float | None:
        """Strip currency symbols / commas and return a float."""
        if not price_str:
            return None
        try:
            cleaned = "".join(ch for ch in price_str.strip() if ch.isdigit() or ch == ".")
            return float(cleaned)
        except (ValueError, TypeError):
            logging.error(json.dumps({
                "event_type": "price_parse_failed",
                "raw_price": price_str,
            }))
            return None

    @abstractmethod
    def extract_info(self, url: str) -> dict:
        """Return ``{'name': str, 'price': float | None}`` for *url*."""


