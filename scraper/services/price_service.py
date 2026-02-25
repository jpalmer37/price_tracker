from datetime import datetime
from scraper.parsers import get_parser

class PriceService:
    def __init__(self, db_service):
        self.db = db_service
    
    def track_price(self, url):
        parser = get_parser(url)
        if parser is None:
            raise ValueError(f"No parser found for URL: {url}")
        info = parser.extract_info(url)
        self.db.add_price_snapshot(url, info['name'], info['price'])