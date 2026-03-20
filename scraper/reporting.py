import logging

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from scraper.database.models import Item, PriceSnapshot, Store
from scraper.logging_utils import log_event
from scraper.notifications import EmailSender


def fetch_latest_snapshots(engine, limit_per_item: int = 5) -> pd.DataFrame:
    with Session(engine) as session:
        rows = session.execute(
            select(
                Item.url.label("item_url"),
                Item.name.label("item_name"),
                Store.name.label("store_name"),
                PriceSnapshot.price.label("price"),
                PriceSnapshot.timestamp.label("timestamp"),
            )
            .join(PriceSnapshot.item)
            .join(Item.store)
            .order_by(Item.url.asc(), PriceSnapshot.timestamp.desc())
        ).all()

    snapshot_frame = pd.DataFrame(rows, columns=["item_url", "item_name", "store_name", "price", "timestamp"])
    if snapshot_frame.empty:
        return snapshot_frame

    snapshot_frame["timestamp"] = pd.to_datetime(snapshot_frame["timestamp"], utc=True)
    snapshot_frame["price"] = pd.to_numeric(snapshot_frame["price"], errors="coerce")
    snapshot_frame = snapshot_frame.sort_values(["item_url", "timestamp"], ascending=[True, False]).reset_index(drop=True)
    snapshot_frame["snapshot_rank"] = snapshot_frame.groupby("item_url").cumcount() + 1

    return snapshot_frame[snapshot_frame["snapshot_rank"] <= limit_per_item].copy()


def detect_notable_price_drops(
    snapshots: pd.DataFrame,
    notable_drop_amount: float = 0,
    notable_drop_percent: float = 10,
) -> pd.DataFrame:
    if snapshots.empty:
        return pd.DataFrame()

    alerts = []
    for _, item_snapshots in snapshots.groupby("item_url"):
        ordered = item_snapshots.sort_values("timestamp", ascending=False).reset_index(drop=True)
        if len(ordered) < 2:
            continue

        latest = ordered.iloc[0]
        comparison_window = ordered.iloc[1:]
        reference_price = comparison_window["price"].max()
        if pd.isna(latest["price"]) or pd.isna(reference_price) or latest["price"] >= reference_price:
            continue

        drop_amount = float(reference_price - latest["price"])
        if reference_price == 0:
            continue

        drop_percent = (drop_amount / float(reference_price)) * 100
        if drop_amount >= notable_drop_amount or drop_percent >= notable_drop_percent:
            alerts.append(
                {
                    "item_url": latest["item_url"],
                    "item_name": latest["item_name"],
                    "store_name": latest["store_name"],
                    "current_price": float(latest["price"]),
                    "reference_price": float(reference_price),
                    "drop_amount": round(drop_amount, 2),
                    "drop_percent": round(drop_percent, 2),
                    "timestamp": latest["timestamp"],
                }
            )

    return pd.DataFrame(alerts)


def build_price_drop_summary(alerts: pd.DataFrame) -> str:
    lines = ["Notable price drops detected:"]
    for _, alert in alerts.iterrows():
        lines.append(
            f"- {alert['item_name']} ({alert['store_name']}): "
            f"${alert['current_price']:.2f} down from ${alert['reference_price']:.2f} "
            f"({alert['drop_percent']:.2f}% / ${alert['drop_amount']:.2f})"
        )

    return "\n".join(lines)


def notify_for_notable_price_drops(engine, notification_config: dict, email_sender_class=EmailSender) -> pd.DataFrame:
    recipients = notification_config.get("recipients") or []
    if not recipients:
        log_event(logging.INFO, "price_drop_notification_skipped", reason="no_recipients")
        return pd.DataFrame()

    latest_snapshots = fetch_latest_snapshots(
        engine,
        limit_per_item=notification_config.get("latest_snapshots_limit", 5),
    )
    alerts = detect_notable_price_drops(
        latest_snapshots,
        notable_drop_amount=notification_config.get("notable_drop_amount", 0),
        notable_drop_percent=notification_config.get("notable_drop_percent", 10),
    )

    if alerts.empty:
        log_event(logging.INFO, "price_drop_notification_skipped", reason="no_alerts")
        return alerts

    sender = email_sender_class(
        sender=notification_config.get("sender", "price-tracker@localhost"),
        recipients=recipients,
        subject=f"Price tracker alert: {len(alerts)} notable price drop(s)",
    )
    sender.send(
        body_text=build_price_drop_summary(alerts),
        html_attachment_path=notification_config.get("html_attachment_path"),
    )
    log_event(logging.INFO, "price_drop_notification_sent", alert_count=len(alerts))
    return alerts
