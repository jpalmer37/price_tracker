from urllib.parse import urlparse

from .base import BaseParser
from .cc_parser import CanadaComputersParser
from .costco_parser import CostcoParser

# Map netloc → parser class
PARSER_MAP: dict[str, type[BaseParser]] = {
    "www.canadacomputers.com": CanadaComputersParser,
    "www.costco.ca": CostcoParser,
}


def get_parser_class(url: str) -> type[BaseParser] | None:
    """Return the parser *class* appropriate for *url*, or ``None``."""
    domain = urlparse(url).netloc
    return PARSER_MAP.get(domain)
