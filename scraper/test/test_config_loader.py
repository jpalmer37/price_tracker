"""Tests for config_loader module."""

import os
import tempfile

import pytest
import yaml

from scraper.config_loader import infer_store_name, load_config


class TestInferStoreName:
    @pytest.mark.parametrize("url,expected", [
        ("https://www.costco.ca/.product.123.html", "costco"),
        ("https://www.canadacomputers.com/en/x.html", "canadacomputers"),
        ("https://www.amazon.ca/dp/B123", "amazon"),
        ("https://bestbuy.com/item/123", "bestbuy"),
    ])
    def test_various_domains(self, url, expected):
        assert infer_store_name(url) == expected


class TestLoadConfig:
    def test_load_valid_yaml(self, tmp_path):
        cfg = {"items": [{"url": "https://example.com/p1"}], "notification": {"recipients": ["a@b.com"]}}
        path = tmp_path / "cfg.yml"
        path.write_text(yaml.dump(cfg))

        loaded = load_config(str(path))
        assert loaded["items"][0]["url"] == "https://example.com/p1"
        assert loaded["notification"]["recipients"] == ["a@b.com"]
