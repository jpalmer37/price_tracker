import pytest
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup

from scraper.parsers.base import BaseParser
from scraper.parsers.costco_parser import CostcoParser
from scraper.parsers.cc_parser import CanadaComputersParser
from scraper.config_loader import infer_store_name
from scraper.database.operations import _extract_store_name, _extract_base_url


# ---------------------------------------------------------------------------
# Fixtures – patch out Selenium so no real browser is launched
# ---------------------------------------------------------------------------
@pytest.fixture
def mock_firefox(monkeypatch):
    """Prevent BaseParser.__init__ from starting a real Firefox session."""
    mock_driver = MagicMock()
    mock_driver.page_source = "<html></html>"

    def _fake_init(self):
        self.driver = mock_driver
        self._soup = None

    monkeypatch.setattr(BaseParser, "__init__", _fake_init)
    return mock_driver


@pytest.fixture
def costco_parser(mock_firefox):
    return CostcoParser()


@pytest.fixture
def cc_parser(mock_firefox):
    return CanadaComputersParser()


# ---------------------------------------------------------------------------
# BaseParser tests
# ---------------------------------------------------------------------------
class TestBaseParser:
    def test_get_name(self, mock_firefox):
        assert CostcoParser.get_name() == "costco"
        assert CanadaComputersParser.get_name() == "canadacomputers"

    def test_find_unique_element_single(self, costco_parser):
        html = "<html><body><span class='test'>Content</span></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        assert costco_parser._find_unique_element(soup, "span", {"class_": "test"}) == "Content"

    def test_find_unique_element_multiple_raises(self, costco_parser):
        html = "<html><body><span class='t'>A</span><span class='t'>B</span></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        with pytest.raises(ValueError):
            costco_parser._find_unique_element(soup, "span", {"class_": "t"})

    def test_find_unique_element_none_raises(self, costco_parser):
        soup = BeautifulSoup("<html><body></body></html>", "html.parser")
        with pytest.raises(ValueError):
            costco_parser._find_unique_element(soup, "span", {"class_": "x"})

    @pytest.mark.parametrize("raw,expected", [
        ("$99.99", 99.99),
        ("$1,234.56", 1234.56),
        ("  $0.50 ", 0.50),
        ("", None),
        (None, None),
    ])
    def test_clean_price(self, raw, expected):
        assert BaseParser.clean_price(raw) == expected

    def test_get_soup_sets_soup(self, costco_parser, mock_firefox):
        mock_firefox.page_source = "<html><body><h1>Hello</h1></body></html>"
        soup = costco_parser._get_soup("http://example.com")
        assert isinstance(soup, BeautifulSoup)
        assert soup.h1.string == "Hello"


# ---------------------------------------------------------------------------
# Costco parser tests
# ---------------------------------------------------------------------------
class TestCostcoParser:
    def test_extract_info(self, costco_parser, mock_firefox):
        mock_firefox.page_source = """
        <html><body>
            <span class="value canada-currency-size" automation-id="productPriceOutput">$99.99</span>
            <h1 itemprop="name" automation-id="productName">Test Product</h1>
        </body></html>
        """
        result = costco_parser.extract_info("http://test.com")
        assert result["name"] == "Test Product"
        assert result["price"] == 99.99


# ---------------------------------------------------------------------------
# Canada Computers parser tests
# ---------------------------------------------------------------------------
class TestCanadaComputersParser:
    def test_extract_info(self, cc_parser, mock_firefox):
        mock_firefox.page_source = """
        <html><body>
            <h1 class="f-20 f-xs-13 fm-SegoeUI-Semibold fm-xs-SF-Pro-Display-Medium h4">GPU Card</h1>
            <span class="current-price-value f-32 f-xs-17 fm-SegoeUI-Bold fm-xs-SF-Pro-Display-Bold font-weight-xs-bold">$799.00</span>
        </body></html>
        """
        result = cc_parser.extract_info("http://test.com")
        assert result["name"] == "GPU Card"
        assert result["price"] == 799.00


# ---------------------------------------------------------------------------
# Config / URL helpers
# ---------------------------------------------------------------------------
class TestConfigHelpers:
    @pytest.mark.parametrize("url,expected", [
        ("https://www.costco.ca/some-product.html", "costco"),
        ("https://www.canadacomputers.com/en/product.html", "canadacomputers"),
        ("https://www.amazon.ca/dp/B0001", "amazon"),
    ])
    def test_infer_store_name(self, url, expected):
        assert infer_store_name(url) == expected


class TestOperationsHelpers:
    @pytest.mark.parametrize("url,expected", [
        ("https://www.costco.ca/product.html", "costco"),
        ("https://www.canadacomputers.com/x", "canadacomputers"),
    ])
    def test_extract_store_name(self, url, expected):
        assert _extract_store_name(url) == expected

    @pytest.mark.parametrize("url,expected", [
        ("https://www.costco.ca/product.html", "www.costco.ca"),
        ("https://www.canadacomputers.com/x", "www.canadacomputers.com"),
    ])
    def test_extract_base_url(self, url, expected):
        assert _extract_base_url(url) == expected
