import logging
import time
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from scraper.logging_utils import log_event

class BaseParser(ABC):

    name = None
    supported_domains = ()

    @classmethod
    def get_name(cls):
        return cls.name

    def __init__(self, browser_service=None, config: dict | None = None):
        self.config = config or {}
        self._owns_driver = browser_service is None
        self.driver = self._resolve_driver(browser_service)

    @classmethod
    def supports_url(cls, url: str) -> bool:
        normalized_url = url.lower()
        return any(domain.lower() in normalized_url for domain in cls.supported_domains)

    def _resolve_driver(self, browser_service=None):
        if browser_service is None:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            driver = webdriver.Firefox(options=options)
        else:
            driver = getattr(browser_service, "driver", browser_service)

        if hasattr(driver, "implicitly_wait"):
            driver.implicitly_wait(self.config.get("implicit_wait_seconds", 10))

        return driver

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def close(self):
        if self._owns_driver and self.driver is not None:
            self.driver.quit()
        self.driver = None


    def _get_soup(self, url):
        try:
            self.driver.get(url)
            time.sleep(self.config.get("page_load_wait_seconds", 5))
            return BeautifulSoup(self.driver.page_source, "html.parser")
        except Exception as exc:
            log_event(logging.ERROR, "page_fetch_failed", url=url, parser=self.get_name(), error=str(exc))
            raise ValueError("Could not fetch BeautifulSoup object") from exc
    
    def _find_unique_element(self, soup, tag, params={}):
        elements = soup.find_all(tag, **params)

        if len(elements) > 1:
            raise ValueError(f"ERROR: Found more than one matching element: {elements}")
        elif len(elements) == 0:    
            raise ValueError("ERROR: Target element not found.")
        
        element = str(elements[0].text)
        element = element.strip()
        return element

    def _find_first_matching_element(self, soup, selectors):
        last_error = None
        for tag, params in selectors:
            try:
                return self._find_unique_element(soup, tag, params)
            except ValueError as exc:
                last_error = exc

        if last_error is not None:
            raise last_error

        raise ValueError("ERROR: Target element not found.")

    def _clean_price(self, price_str: str) -> float | None:
        """Helper to clean common price string issues ($, commas)."""
        if not price_str:
            return None
        try:
            # Remove currency symbols, commas, whitespace
            cleaned = ''.join(filter(lambda x: x.isdigit() or x == '.', price_str.strip()))
            return float(cleaned)
        except (ValueError, TypeError):
            log_event(logging.ERROR, "price_parse_failed", parser=self.get_name(), price_string=price_str)
            return None    

    @abstractmethod
    def extract_info(self, url):
        pass
