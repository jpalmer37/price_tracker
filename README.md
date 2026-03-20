# price_tracker

A Selenium + PostgreSQL price tracker that scrapes supported stores with a headless Firefox browser, stores historical price snapshots with SQLAlchemy, and can emit JSONL-friendly logs plus notable price-drop email alerts.

## Configuration

Update `scraper/config.yml` with:

- `items`: a flat list of product URLs to track
- `notification.recipients`: the email addresses that should receive alerts
- optional notification thresholds such as `notable_drop_amount`, `notable_drop_percent`, and `latest_snapshots_limit`

The application infers the store parser directly from each item URL.

## Local run

1. Set database environment variables:
   - `DATABASE_USERNAME`
   - `DATABASE_PASSWORD`
   - `DATABASE_HOST`
   - `DATABASE_PORT`
   - `DATABASE_NAME`

   Alternatively, set `DATABASE_URL` directly.

2. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Run the scraper:

   ```bash
   python -m scraper.main -c scraper/config.yml
   ```

## Docker

The repository includes two Dockerized services:

- `postgres`: the PostgreSQL database
- `price-tracker`: the scraper / notification application

Start both with:

```bash
docker compose -f env/docker-compose.yml up --build
```

## Notifications

The reporting pipeline uses pandas + SQLAlchemy to load the latest `N` snapshots per item, detect notable price drops, and send alert emails through the local `sendmail` binary. HTML report attachments are supported through the notification configuration.
