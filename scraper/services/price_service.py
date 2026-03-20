from scraper.parsers import get_parser_class_for_url

class PriceService:
    def __init__(self, db_service):
        self.db = db_service
    
    def track_price(self, url):
        parser_class = get_parser_class_for_url(url)
        with parser_class() as parser:
            info = parser.extract_info(url)
        self.db.add_price_snapshot(url, info['name'], info['price'])
