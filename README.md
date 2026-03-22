# Price Tracker

A Dockerized price-tracking application that scrapes product pages using a headless Firefox browser (Selenium), stores historical price snapshots in a single SQLite database file (via SQLAlchemy), and sends email alerts when notable price drops are detected.

## Architecture

| Container | Purpose |
|-----------|---------|
| **tracker** | Python application that scrapes prices on a cron schedule, records snapshots in SQLite, analyses trends, and sends email notifications |

## Quick Start

```bash
# 1. Clone and enter the repo
git clone https://github.com/jpalmer37/price_tracker.git
cd price_tracker

# 2. (Optional) Create a .env file with a custom SQLite database path
cat > .env <<'EOF'
DATABASE_PATH=/data/price_tracker.db
EOF

# 3. Edit the watchlist
#    Add the product URLs you want to track in scraper/config.yml

# 4. Build and run the cron-driven container
cd env
docker compose up --build
```

The container keeps running in the foreground and executes the scraper every 12 hours via cron. The SQLite database file is persisted in a Docker volume mounted at `/data`.

## Python Environment Options

Use either pip or conda:

```bash
# pip
pip install -r requirements.txt
```

```bash
# conda
conda env create -f environment.yml
conda activate price-tracker
```

## Configuration

Edit `scraper/config.yml` to define the items to track and notification settings:

```yaml
notification:
  sender: "pricetracker@example.com"
  recipients:
    - "you@example.com"

price_drop_threshold_pct: 10.0
snapshot_lookback: 5

items:
  - url: https://www.costco.ca/.product.4000092152.html
  - url: https://www.canadacomputers.com/en/some-product.html
```

The application automatically determines which store a URL belongs to from the domain name—no need to specify the store manually.

## Running Tests

```bash
pip install -r requirements.txt
pip install pytest
python -m pytest scraper/test/ -v
```

## Project Layout

```
├── Dockerfile                  # App container image
├── environment.yml             # Conda environment definition
├── price-tracker.cron          # Cron schedule used by the container
├── requirements.txt            # Python dependencies
├── env/
│   └── docker-compose.yml      # Orchestrates the cron-driven tracker container
└── scraper/
    ├── main.py                 # Entry point
    ├── config.yml              # Watchlist & notification config
    ├── config_loader.py        # YAML loading & store inference
    ├── logging_utils.py        # Centralised JSON logging
    ├── notifications.py        # EmailSender class (sendmail)
    ├── price_analysis.py       # Pandas-based drop detection & alerts
    ├── database/
    │   ├── config.py           # SQLite DB connection URL from env vars
    │   ├── database.py         # Engine & session management
    │   ├── models.py           # SQLAlchemy models (Store, Item, PriceSnapshot)
    │   └── operations.py       # CRUD helpers
    ├── parsers/
    │   ├── base.py             # Abstract parser with Selenium + BS4
    │   ├── costco_parser.py    # Costco-specific extraction
    │   └── cc_parser.py        # Canada Computers extraction
    └── test/
        └── test_parser.py      # Unit tests
```
