import argparse
import logging

from scraper.config_loader import load_config
from scraper.database.database import Database
from scraper.database.operations import add_price_snapshot
from scraper.logging_utils import log_event, setup_json_logging
from scraper.parsers import get_parser_class_for_url
from scraper.reporting import notify_for_notable_price_drops


def init_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, required=True)
    parser.add_argument("--skip-notifications", action="store_true")
    return parser


def scrape_sites(config):
    log_event(logging.INFO, "scrape_started", item_count=len(config["items"]))
    item_data = {}

    items_by_store = {}
    for item in config["items"]:
        items_by_store.setdefault(item["store_name"], []).append(item)

    for store_name, store_items in items_by_store.items():
        parser_class = get_parser_class_for_url(store_items[0]["url"])
        parser_config = {"page_load_wait_seconds": config.get("page_load_wait_seconds", 5)}

        log_event(logging.INFO, "store_scrape_started", store_name=store_name, item_count=len(store_items))
        with parser_class(config=parser_config) as parser:
            for item in store_items:
                info = parser.extract_info(item["url"])
                item_data[item["url"]] = {
                    "store_name": store_name,
                    "name": info.get("name") or item.get("name"),
                    "price": info.get("price"),
                }
                log_event(
                    logging.INFO,
                    "item_scraped",
                    item_url=item["url"],
                    store_name=store_name,
                    item_name=item_data[item["url"]]["name"],
                    price=item_data[item["url"]]["price"],
                )

    return item_data


def save_snapshots(item_data, session):
    for url, item in item_data.items():
        add_price_snapshot(session, url, item["name"], item["price"])


def main():
    setup_json_logging()

    arg_parser = init_parser()
    args = arg_parser.parse_args()

    config = load_config(args.config)
    log_event(logging.INFO, "config_loaded", config_path=args.config, item_count=len(config["items"]))

    database = Database()
    database.create_all()

    item_data = scrape_sites(config)
    with database.get_session() as session:
        save_snapshots(item_data, session)

    if not args.skip_notifications:
        notify_for_notable_price_drops(database.engine, config["notification"])

    log_event(logging.INFO, "scrape_completed", saved_snapshot_count=len(item_data))


if __name__ == "__main__":
    main()
