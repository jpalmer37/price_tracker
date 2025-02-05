from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
from abc import ABC, abstractmethod

class BaseParser(ABC):

    name = None
    browser = None
    driver = None

    @classmethod
    def get_name(cls):
        return cls.name

    def __init__(self, browser_service):
        self.browser = browser_service
        self.driver = browser_service.driver

    def _fetch_page_soup(self, url):
        try:
            self.driver.get(url)
            return BeautifulSoup(self.driver.page_source, 'html.parser')
        except Exception as e:
            print(e)
            raise ValueError('Could not fetch BeautifulSoup object')
    
    def _find_unique_element(self, soup, tag, params={}):
        elements = soup.find_all(tag, **params)
        if len(elements) > 1:
            raise ValueError("ERROR: Found more than one matching price value ")
        elif len(elements) == 0:    
            raise ValueError("ERROR: Price value not found.")
        return str(elements[0].text)
    @abstractmethod
    def extract_info(self, url):
        pass

