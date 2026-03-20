from urllib.parse import urlparse

from .cc_parser import CanadaComputersParser
from .costco_parser import CostcoParser

PARSER_CLASSES = (CostcoParser, CanadaComputersParser)


def normalize_hostname(url: str) -> str:
    hostname = urlparse(url).hostname or ""
    return hostname.lower().removeprefix("www.")


def get_parser_class_for_url(url: str):
    hostname = normalize_hostname(url)
    for parser_class in PARSER_CLASSES:
        for supported_domain in parser_class.supported_domains:
            domain = supported_domain.lower().removeprefix("www.")
            if hostname == domain or hostname.endswith(f".{domain}"):
                return parser_class
    raise ValueError(f"No parser found for URL: {url}")


def infer_store_name(url: str) -> str:
    return get_parser_class_for_url(url).get_name()
