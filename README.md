# Price Tracker

A Dockerized price-tracking application that scrapes product pages using a headless Firefox browser (Selenium), stores historical price snapshots in PostgreSQL (via SQLAlchemy), and sends email alerts when notable price drops are detected.

## Architecture

| Container | Purpose |
|-----------|---------|
| **postgres** | PostgreSQL 14 database holding `stores`, `items`, and `price_snapshots` tables |
| **tracker** | Python application that scrapes prices, records snapshots, analyses trends, and sends email notifications |

## Quick Start

```bash
# 1. Clone and enter the repo
git clone https://github.com/jpalmer37/price_tracker.git
cd price_tracker

# 2. (Optional) Create a .env file with your database credentials
#    Defaults are provided in docker-compose.yml
cat > .env <<'EOF'
DATABASE_USERNAME=dbuser
DATABASE_PASSWORD=S3cret
DATABASE_NAME=price_tracker
EOF

# 3. Edit the watchlist
#    Add the product URLs you want to track in scraper/config.yml

# 4. Build and run
cd env
docker compose up --build
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
python -m pytest scraper/test/ -v
```

## Project Layout

```
├── Dockerfile                  # App container image
├── requirements.txt            # Python dependencies
├── env/
│   └── docker-compose.yml      # Orchestrates postgres + tracker
└── scraper/
    ├── main.py                 # Entry point
    ├── config.yml              # Watchlist & notification config
    ├── config_loader.py        # YAML loading & store inference
    ├── logging_utils.py        # Centralised JSON logging
    ├── notifications.py        # EmailSender class (sendmail)
    ├── price_analysis.py       # Pandas-based drop detection & alerts
    ├── database/
    │   ├── config.py           # DB connection URL from env vars
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

