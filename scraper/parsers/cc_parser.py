from .base import BaseParser
import logging 

class CanadaComputersParser(BaseParser):

    name = 'canada_computers'
    
    def extract_price(self, url):
        soup = self._fetch_page_soup(url)
        price = self._find_unique_element(soup, "h1", {'class_':"f-20 f-xs-13 fm-SegoeUI-Semibold fm-xs-SF-Pro-Display-Medium h4"})
        name = self._find_unique_element(soup, "div", {'class_':"current-price-value f-32 f-xs-17 fm-SegoeUI-Bold fm-xs-SF-Pro-Display-Bold font-weight-xs-bold"})

        return price 


