from .base import BaseParser
import logging 

class CostcoParser(BaseParser):

    name = 'costco'

    def extract_info(self, url):
        soup = self._fetch_page_soup(url)
        price = self._find_unique_element(soup, "span", {'class_':"value canada-currency-size"})
        name = self._find_unique_element(soup, "h1", {'attr':{"itemprop":"name", 'automation-id':'productName'}})

        return {'name': name, 'price': price} 
