from .base import BaseParser
import logging 

class CostcoParser(BaseParser):

    name = 'costco'

    def extract_info(self, url):
        soup = self._get_soup(url)
        price = self._find_unique_element(soup, "span", {'class_':"value canada-currency-size", 'automation-id':'productPriceOutput'})
        name = self._find_unique_element(soup, "h1", {"itemprop":"name", 'automation-id':'productName'})

        return {'name': name, 'price': price} 
