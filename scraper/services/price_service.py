from datetime import datetime

class PriceService:
    def __init__(self, db_service, parsers):
        self.db = db_service
        self.parsers = parsers
    
    def get_scraper_for_url(self, url):
        for parser in self.parsers:
            if parser.validate_url(url):
                return parser
        raise ValueError("No scraper found for URL")
    
    def track_price(self, url):
        scraper = self.get_scraper_for_url(url)
        price = scraper.get_price(url)
        name = scraper.get_product_name(url)
        
        product = self.db.update_product(url, name, price)
        self.db.add_price_history(product.id, price)