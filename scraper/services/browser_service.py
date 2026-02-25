from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from contextlib import contextmanager

class BrowserManager:
    def __init__(self):
        self.options = Options()
        self.options.add_argument('--headless')
        
    @contextmanager
    def browser_scope(self):
        """Provide a context for browser operations with automatic cleanup."""
        browser = webdriver.Firefox(options=self.options)
        try:
            yield browser
        finally:
            browser.quit()
