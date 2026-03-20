from datetime import datetime, timedelta, timezone
from decimal import Decimal

import yaml

from scraper.config_loader import load_config
from scraper.database.database import Database
from scraper.database.models import Item, PriceSnapshot, Store
from scraper.database.operations import add_price_snapshot, get_item_history
from scraper.notifications import EmailSender
from scraper.reporting import (
    fetch_latest_snapshots,
    notify_for_notable_price_drops,
)


def test_load_config_infers_store_names_and_supports_legacy_watchlist(tmp_path):
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "watchlist_by_store": {
                    "costco": [{"url": "https://www.costco.ca/product.html", "name": "Protein"}],
                    "canada_computers": [{"url": "https://www.canadacomputers.com/product.html"}],
                },
                "email_recipients": ["alerts@example.com"],
            }
        ),
        encoding="utf-8",
    )

    config = load_config(str(config_path))

    assert sorted(item["store_name"] for item in config["items"]) == ["canada_computers", "costco"]
    assert config["notification"]["recipients"] == ["alerts@example.com"]


def test_add_price_snapshot_creates_store_item_and_history():
    database = Database(database_url="sqlite+pysqlite:///:memory:")
    database.create_all()

    with database.get_session() as session:
        add_price_snapshot(session, "https://www.costco.ca/product.html", "Protein", "$99.99")
        item = session.query(Item).filter(Item.url == "https://www.costco.ca/product.html").one()
        store = session.query(Store).filter(Store.id == item.store_id).one()
        history = get_item_history(session, item.id, limit=5)

    assert store.name == "costco"
    assert store.base_url == "costco.ca"
    assert item.name == "Protein"
    assert len(history) == 1
    assert float(history[0].price) == 99.99


def test_notify_for_notable_price_drops_sends_summary_email():
    database = Database(database_url="sqlite+pysqlite:///:memory:")
    database.create_all()

    now = datetime.now(timezone.utc)
    with database.get_session() as session:
        store = Store(name="costco", base_url="https://www.costco.ca")
        item = Item(name="Protein", url="https://www.costco.ca/product.html", store=store, is_active=True)
        session.add_all(
            [
                store,
                item,
                PriceSnapshot(item=item, price=Decimal("120.00"), timestamp=now - timedelta(days=2)),
                PriceSnapshot(item=item, price=Decimal("110.00"), timestamp=now - timedelta(days=1)),
                PriceSnapshot(item=item, price=Decimal("90.00"), timestamp=now),
            ]
        )

    sent_messages = []

    class FakeEmailSender:
        def __init__(self, sender, recipients, subject, sendmail_path="/usr/sbin/sendmail"):
            self.sender = sender
            self.recipients = recipients
            self.subject = subject

        def send(self, body_text=None, html_attachment_path=None):
            sent_messages.append(
                {
                    "sender": self.sender,
                    "recipients": self.recipients,
                    "subject": self.subject,
                    "body_text": body_text,
                    "html_attachment_path": html_attachment_path,
                }
            )
            return True

    alerts = notify_for_notable_price_drops(
        database.engine,
        {
            "sender": "price-tracker@localhost",
            "recipients": ["alerts@example.com"],
            "latest_snapshots_limit": 5,
            "notable_drop_amount": 15,
            "notable_drop_percent": 10,
        },
        email_sender_class=FakeEmailSender,
    )

    latest_snapshots = fetch_latest_snapshots(database.engine, limit_per_item=5)

    assert len(latest_snapshots) == 3
    assert len(alerts) == 1
    assert alerts.iloc[0]["item_name"] == "Protein"
    assert sent_messages and "Notable price drops detected" in sent_messages[0]["body_text"]


def test_email_sender_build_message_attaches_html_file(tmp_path):
    html_report = tmp_path / "report.html"
    html_report.write_text("<html><body>report</body></html>", encoding="utf-8")

    sender = EmailSender(
        sender="price-tracker@localhost",
        recipients=["alerts@example.com"],
        subject="Price tracker alert",
    )

    message = sender._build_message(html_attachment_path=str(html_report))

    assert len(message.get_payload()) == 2
    assert "report.html" in message.as_string()
