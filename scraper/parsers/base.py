from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
from abc import ABC, abstractmethod
import logging 

class BaseParser(ABC):

    name = None

    @classmethod
    def get_name(cls):
        return cls.name

    def __init__(self, config: dict = None):
        self.config = config or {}

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(10)
        self.soup = None


    def _get_soup(self, url):
        if not self.soup: 
            try:
                self.driver.get(url)
                time.sleep(5)
                self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            except Exception as e:
                print(e)
                raise ValueError('Could not fetch BeautifulSoup object')
        return self.soup
    
    def _find_unique_element(self, soup, tag, params={}):
        elements = soup.find_all(tag, **params)

        if len(elements) > 1:
            logging.warning(f"WARNING: Found more than one matching element: {elements}")
        elif len(elements) == 0:    
            raise ValueError("ERROR: Target element not found.")
        
        element = str(elements[0].text)
        element = element.strip()
        return element

    def _clean_price(self, price_str: str) -> float | None:
        """Helper to clean common price string issues ($, commas)."""
        if not price_str:
            return None
        try:
            # Remove currency symbols, commas, whitespace
            cleaned = ''.join(filter(lambda x: x.isdigit() or x == '.', price_str.strip()))
            return float(cleaned)
        except (ValueError, TypeError):
            logging.error(f"Could not parse price string: {price_str}") # Use logging
            return None    

    @abstractmethod
    def extract_info(self, url):
        pass

