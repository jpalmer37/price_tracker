#%%
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import argparse 
import os, pandas as pd 
from collections import defaultdict
import numpy as np 
import re 
import json
import time 
import logging 

from scraper_costco.scraper.database.operations import Database
from parsers.costco_parser import CostcoParser
from parsers.cc_parser import CanadaComputersParser

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
        return json.load(f)

#%%
def scrape_sites(config):
    logging.info(json.dumps({"event_type": "start_scrape"}))
    item_data = []

    for store_name, store_item_list in config['watchlist_by_store'].items():

        logging.info()

        store_parser_class = store_class_map[store_name]

        with store_parser_class() as parser:

            for item in store_item_list:

                soup = parser.fetch_page_soup(item['item_url'])

                price = parser.extract_price(soup)

                # item_data[item['url']] = item
                # item_data[item['url']]['store_name'] = store_name
                # item_data[item['url']]['price'] = price

    return item_data


def save_snapshots(item_data, database):
    for url, item in item_data.items():
        database.add_price_snapshot(item)
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

    parser = init_parser()

    args = parser.parse_args()

    config = load_config(args.config)

    item_data = scrape_sites(config)

#%%
if __name__ == '__main__':
    main()
