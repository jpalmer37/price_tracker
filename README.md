# price_tracker

A price tracking scraper that monitors product prices from Costco and Canada Computers, storing historical snapshots in a PostgreSQL database.

## Setup

1. Copy `.env` and fill in your database credentials (`DATABASE_USERNAME`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`).
2. Edit `scraper/config.yml` to add the products you want to track under `watchlist_by_store`.
3. Run the scraper: `python -m scraper.main -c scraper/config.yml`
