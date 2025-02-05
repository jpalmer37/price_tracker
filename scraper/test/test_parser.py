import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup
from ..parsers.base import BaseParser

# Fixtures
@pytest.fixture
def mock_browser_service():
    service = Mock()
    service.driver = Mock()
    return service

@pytest.fixture
def costco_parser(mock_browser_service):
    return CostcoParser(mock_browser_service)

@pytest.fixture
def canada_computers_parser(mock_browser_service):
    return CanadaComputersParser(mock_browser_service)

# Base Parser Tests
def test_get_name():
    class TestParser(BaseParser):
        name = 'test_parser'
    
    assert TestParser.get_name() == 'test_parser'

def test_fetch_page_soup(mock_browser_service):
    parser = CostcoParser(mock_browser_service)
    test_html = "<html><body><h1>Test Page</h1></body></html>"
    parser.driver.page_source = test_html
    
    soup = parser._fetch_page_soup("http://test.com")
    assert isinstance(soup, BeautifulSoup)
    assert str(soup.h1.string) == "Test Page"

def test_find_unique_element(costco_parser):
    # Test with single element
    html = "<html><body><span class='test'>Content</span></body></html>"
    soup = BeautifulSoup(html, 'html.parser')
    result = costco_parser._find_unique_element(soup, "span", {'class_': 'test'})
    assert result == "Content"

def test_find_unique_element_multiple_raises(costco_parser):
    # Test with multiple elements
    html = "<html><body><span class='test'>Content1</span><span class='test'>Content2</span></body></html>"
    soup = BeautifulSoup(html, 'html.parser')
    with pytest.raises(ValueError):
        costco_parser._find_unique_element(soup, "span", {'class_': 'test'})

def test_find_unique_element_none_raises(costco_parser):
    # Test with no elements
    html = "<html><body></body></html>"
    soup = BeautifulSoup(html, 'html.parser')
    with pytest.raises(ValueError):
        costco_parser._find_unique_element(soup, "span", {'class_': 'test'})

# Costco Parser Tests
def test_costco_extract_info(_, costco_parser):
    test_html = """
    <html>
        <body>
            <span class="value canada-currency-size">$99.99</span>
            <h1 itemprop="name" automation-id="productName">Test Product</h1>
        </body>
    </html>
    """
    costco_parser.driver.page_source = test_html
    
    result = costco_parser.extract_info("http://test.com")
    assert result['price'] == "$99.99"
    assert result['name'] == "Test Product"

# Canada Computers Parser Tests
def test_canada_computers_extract_price(_, canada_computers_parser):
    test_html = """
    <html>
        <body>
            <h1 class="f-20 f-xs-13 fm-SegoeUI-Semibold fm-xs-SF-Pro-Display-Medium h4">Test Product</h1>
            <div class="current-price-value f-32 f-xs-17 fm-SegoeUI-Bold fm-xs-SF-Pro-Display-Bold font-weight-xs-bold">$199.99</div>
        </body>
    </html>
    """
    canada_computers_parser.driver.page_source = test_html
    
    result = canada_computers_parser.extract_price("http://test.com")
    assert result == "$199.99"

# Parameterized Tests Example
@pytest.mark.parametrize("url,expected_price,expected_name", [
    ("http://costco.com/product1", "$99.99", "Product 1"),
    ("http://costco.com/product2", "$199.99", "Product 2"),
])
def test_costco_extract_info_parametrized(costco_parser, url, expected_price, expected_name):
    test_html = f"""
    <html>
        <body>
            <span class="value canada-currency-size">{expected_price}</span>
            <h1 itemprop="name" automation-id="productName">{expected_name}</h1>
        </body>
    </html>
    """
    costco_parser.driver.page_source = test_html
    
    result = costco_parser.extract_info(url)
    assert result['price'] == expected_price
    assert result['name'] == expected_name