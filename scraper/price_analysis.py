"""Analyse recent price snapshots and send email alerts on notable drops."""

import json
import logging
from decimal import Decimal

import pandas as pd
from sqlalchemy.orm import Session

from .database.models import Item, PriceSnapshot, Store
from .notifications import EmailSender


def get_recent_snapshots(session: Session, lookback: int = 5) -> pd.DataFrame:
    """Pull the latest *lookback* snapshots per active item into a DataFrame."""
    items = session.query(Item).filter(Item.is_active.is_(True)).all()

    rows: list[dict] = []
    for item in items:
        snapshots = (
            session.query(PriceSnapshot)
            .filter(PriceSnapshot.item_id == item.id)
            .order_by(PriceSnapshot.timestamp.desc())
            .limit(lookback)
            .all()
        )
        store = session.query(Store).filter(Store.id == item.store_id).first()
        for snap in snapshots:
            rows.append({
                "item_id": item.id,
                "item_name": item.name,
                "url": item.url,
                "store": store.name if store else "unknown",
                "price": float(snap.price) if snap.price is not None else None,
                "timestamp": snap.timestamp,
            })

    return pd.DataFrame(rows)


def detect_price_drops(
    df: pd.DataFrame, threshold_pct: float = 10.0
) -> pd.DataFrame:
    """Return rows where the latest price dropped ≥ *threshold_pct* % vs the previous mean.

    For each item the function compares the most recent price against the
    average of all *older* snapshots in the window.  If the current price is
    lower by at least *threshold_pct* %, the item is flagged.
    """
    alerts: list[dict] = []

    for item_id, group in df.groupby("item_id"):
        group = group.sort_values("timestamp", ascending=False)
        if len(group) < 2:
            continue

        latest_price = group.iloc[0]["price"]
        if latest_price is None:
            continue

        older_prices = group.iloc[1:]["price"].dropna()
        if older_prices.empty:
            continue

        avg_older = older_prices.mean()
        if avg_older == 0:
            continue

        drop_pct = ((avg_older - latest_price) / avg_older) * 100
        if drop_pct >= threshold_pct:
            alerts.append({
                "item_id": item_id,
                "item_name": group.iloc[0]["item_name"],
                "url": group.iloc[0]["url"],
                "store": group.iloc[0]["store"],
                "latest_price": latest_price,
                "avg_previous_price": round(avg_older, 2),
                "drop_pct": round(drop_pct, 2),
            })

    alert_df = pd.DataFrame(alerts)
    if not alert_df.empty:
        logging.info(json.dumps({
            "event_type": "price_drops_detected",
            "count": len(alert_df),
        }))
    return alert_df


def send_price_drop_alerts(
    alert_df: pd.DataFrame,
    sender: str,
    recipients: list[str],
) -> None:
    """Format and email price-drop alerts."""
    if alert_df.empty:
        logging.info(json.dumps({"event_type": "no_price_drops"}))
        return

    lines = ["Price-drop alerts:\n"]
    for _, row in alert_df.iterrows():
        lines.append(
            f"  • {row['item_name']} ({row['store']}): "
            f"${row['latest_price']:.2f} (was ~${row['avg_previous_price']:.2f}, "
            f"down {row['drop_pct']:.1f}%)\n"
            f"    {row['url']}"
        )

    body = "\n".join(lines)

    mailer = EmailSender(
        sender=sender,
        recipients=recipients,
        subject="Price Tracker – Price Drop Alert",
    )
    mailer.send(body_text=body)


def check_and_notify(
    session: Session,
    config: dict,
) -> None:
    """Top-level convenience: pull snapshots, detect drops, and email if any."""
    lookback = config.get("snapshot_lookback", 5)
    threshold = config.get("price_drop_threshold_pct", 10.0)
    notification = config.get("notification", {})

    df = get_recent_snapshots(session, lookback=lookback)
    if df.empty:
        logging.info(json.dumps({"event_type": "no_snapshots_for_analysis"}))
        return

    alerts = detect_price_drops(df, threshold_pct=threshold)
    send_price_drop_alerts(
        alerts,
        sender=notification.get("sender", "pricetracker@example.com"),
        recipients=notification.get("recipients", []),
    )
