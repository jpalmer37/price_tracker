from .base import BaseParser

class CostcoParser(BaseParser):

    name = 'costco'
    supported_domains = ("costco.ca", "costco.com")

    def extract_info(self, url):
        soup = self._get_soup(url)
        price = self._find_first_matching_element(
            soup,
            [
                ("span", {"automation-id": "productPriceOutput"}),
                ("span", {"class_": "value canada-currency-size"}),
            ],
        )
        name = self._find_first_matching_element(
            soup,
            [
                ("h1", {"itemprop": "name", "automation-id": "productName"}),
                ("h1", {"itemprop": "name"}),
            ],
        )

        return {'name': name, 'price': price} 
