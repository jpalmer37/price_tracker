"""Tests for price_analysis module."""

import pytest
import pandas as pd

from scraper.price_analysis import detect_price_drops


class TestDetectPriceDrops:
    def _make_df(self, rows):
        return pd.DataFrame(rows)

    def test_no_drop_when_price_stable(self):
        rows = [
            {"item_id": 1, "item_name": "A", "url": "http://a", "store": "s",
             "price": 100.0, "timestamp": pd.Timestamp("2025-01-03")},
            {"item_id": 1, "item_name": "A", "url": "http://a", "store": "s",
             "price": 100.0, "timestamp": pd.Timestamp("2025-01-02")},
            {"item_id": 1, "item_name": "A", "url": "http://a", "store": "s",
             "price": 100.0, "timestamp": pd.Timestamp("2025-01-01")},
        ]
        alerts = detect_price_drops(self._make_df(rows), threshold_pct=10.0)
        assert alerts.empty

    def test_detects_large_drop(self):
        rows = [
            {"item_id": 1, "item_name": "A", "url": "http://a", "store": "s",
             "price": 50.0, "timestamp": pd.Timestamp("2025-01-03")},
            {"item_id": 1, "item_name": "A", "url": "http://a", "store": "s",
             "price": 100.0, "timestamp": pd.Timestamp("2025-01-02")},
            {"item_id": 1, "item_name": "A", "url": "http://a", "store": "s",
             "price": 100.0, "timestamp": pd.Timestamp("2025-01-01")},
        ]
        alerts = detect_price_drops(self._make_df(rows), threshold_pct=10.0)
        assert len(alerts) == 1
        assert alerts.iloc[0]["drop_pct"] == 50.0

    def test_ignores_small_drop(self):
        rows = [
            {"item_id": 1, "item_name": "A", "url": "http://a", "store": "s",
             "price": 95.0, "timestamp": pd.Timestamp("2025-01-03")},
            {"item_id": 1, "item_name": "A", "url": "http://a", "store": "s",
             "price": 100.0, "timestamp": pd.Timestamp("2025-01-02")},
        ]
        alerts = detect_price_drops(self._make_df(rows), threshold_pct=10.0)
        assert alerts.empty

    def test_single_snapshot_no_alert(self):
        rows = [
            {"item_id": 1, "item_name": "A", "url": "http://a", "store": "s",
             "price": 50.0, "timestamp": pd.Timestamp("2025-01-01")},
        ]
        alerts = detect_price_drops(self._make_df(rows), threshold_pct=10.0)
        assert alerts.empty

    def test_empty_dataframe(self):
        df = pd.DataFrame(columns=["item_id", "item_name", "url", "store", "price", "timestamp"])
        alerts = detect_price_drops(df)
        assert alerts.empty
