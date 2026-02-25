# parsers/__init__.py
from urllib.parse import urlparse
from .base import BaseParser
from .cc_parser import CanadaComputersParser
from .costco_parser import CostcoParser
# Import other parsers

# Map domain names to parser classes
PARSER_MAP = {
    'www.canadacomputers.com': CanadaComputersParser,
    'www.costco.ca': CostcoParser,
    # Add other domains (e.g., 'www.amazon.ca', 'www.bestbuy.com')
}

def get_parser(url: str) -> BaseParser | None:
    """
    Factory function to return the appropriate parser instance based on the URL's domain.
    """
    try:
        domain = urlparse(url).netloc
        parser_class = PARSER_MAP.get(domain)
        if parser_class:
            return parser_class()
        else:
            print(f"No parser found for domain: {domain}") # Use logging
            return None
    except Exception as e:
        print(f"Error determining parser for {url}: {e}") # Use logging
        return None