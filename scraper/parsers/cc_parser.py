from .base import BaseParser


class CanadaComputersParser(BaseParser):

    name = "canadacomputers"

    def extract_info(self, url: str) -> dict:
        soup = self._get_soup(url)
        name = self._find_unique_element(
            soup,
            "h1",
            {"class_": "f-20 f-xs-13 fm-SegoeUI-Semibold fm-xs-SF-Pro-Display-Medium h4"},
        )
        raw_price = self._find_unique_element(
            soup,
            "span",
            {"class_": "current-price-value f-32 f-xs-17 fm-SegoeUI-Bold fm-xs-SF-Pro-Display-Bold font-weight-xs-bold"},
        )
        return {"name": name, "price": self.clean_price(raw_price)}
    


