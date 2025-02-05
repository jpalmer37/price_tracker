from selenium import webdriver
from selenium.webdriver.firefox.options import Options

class BrowserService:
    """
    A service class responsible for everything related to selenium browser sessions.
    """
    def __init__(self):
        self.options = Options()
        self.options.add_argument('--headless')
        self.driver = None
        
    def __enter__(self):
        if not self.driver:
            self.driver = webdriver.Firefox(options=self.options)
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.quit()
            self.driver = None
