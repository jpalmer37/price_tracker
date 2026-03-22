"""Price-tracker application entry point."""

import argparse
import json
import logging
from collections import defaultdict

from scraper.config_loader import infer_store_name, load_config
from scraper.database.database import Database
from scraper.database.operations import add_price_snapshot
from scraper.logging_utils import setup_json_logging
from scraper.parsers import get_parser_class
from scraper.price_analysis import check_and_notify


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Price Tracker")
    parser.add_argument("-c", "--config", type=str, required=True, help="Path to config YAML")
    return parser


def scrape_items(config: dict) -> list[dict]:
    """Scrape every item listed in *config* and return enriched dicts."""
    items = config.get("items", [])

    # Group items by parser class so we open one browser per store.
    groups: dict[type, list[dict]] = defaultdict(list)
    for item in items:
        url = item["url"]
        parser_cls = get_parser_class(url)
        if parser_cls is None:
            logging.warning(json.dumps({
                "event_type": "no_parser_for_url",
                "url": url,
            }))
            continue
        groups[parser_cls].append(item)

    results: list[dict] = []
    for parser_cls, group_items in groups.items():
        with parser_cls() as parser:
            for item in group_items:
                url = item["url"]
                try:
                    info = parser.extract_info(url)
                    results.append({
                        "url": url,
                        "store_name": infer_store_name(url),
                        "name": info["name"],
                        "price": info["price"],
                    })
                    logging.info(json.dumps({
                        "event_type": "item_scraped",
                        "url": url,
                        "name": info["name"],
                        "price": str(info["price"]),
                    }))
                except Exception as exc:
                    logging.error(json.dumps({
                        "event_type": "item_scrape_failed",
                        "url": url,
                        "error": str(exc),
                    }))
    return results


def save_snapshots(results: list[dict], session) -> None:
    """Persist scraped price data as PriceSnapshot rows."""
    for item in results:
        add_price_snapshot(session, item["url"], item["name"], item["price"])


def main() -> None:
    setup_json_logging()

    args = _build_arg_parser().parse_args()
    config = load_config(args.config)

    database = Database()
    database.create_tables()

    results = scrape_items(config)

    with database.get_session() as session:
        save_snapshots(results, session)

    # After scraping, check for price drops and notify
    with database.get_session() as session:
        check_and_notify(session, config)

    logging.info(json.dumps({"event_type": "run_complete", "items_scraped": len(results)}))


if __name__ == "__main__":
    main()

