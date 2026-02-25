#%%
import argparse 
import yaml
import logging 

from scraper.database.database import Database
from scraper.database.operations import add_price_snapshot
from scraper.parsers.costco_parser import CostcoParser
from scraper.parsers.cc_parser import CanadaComputersParser

store_class_map = [
    CostcoParser, 
    CanadaComputersParser
]
store_class_map = dict(zip([x.get_name() for x in store_class_map], store_class_map))

def init_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type=str, required=True)
    return parser

def load_config(config_file):
    with open(config_file) as f:
        return yaml.safe_load(f)

#%%
def scrape_sites(config):
    logging.info("Starting scrape")
    item_data = {}

    for store_name, store_item_list in config['watchlist_by_store'].items():

        logging.info(f"Scraping store: {store_name}")

        store_parser_class = store_class_map[store_name]

        with store_parser_class() as parser:

            for item in store_item_list:

                info = parser.extract_info(item['url'])

                item_data[item['url']] = item
                item_data[item['url']]['store_name'] = store_name
                item_data[item['url']]['price'] = info['price']
                item_data[item['url']]['name'] = info['name']

    return item_data


def save_snapshots(item_data, session):
    for url, item in item_data.items():
        add_price_snapshot(session, url, item['name'], item['price'])

def main():
    logging.basicConfig(
        filename='scraper.log',
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("debug.log"),
            logging.StreamHandler()
        ]
    )

    arg_parser = init_parser()

    args = arg_parser.parse_args()

    config = load_config(args.config)

    database = Database()
    item_data = scrape_sites(config)
    with database.get_session() as session:
        save_snapshots(item_data, session)

#%%
if __name__ == '__main__':
    main()
