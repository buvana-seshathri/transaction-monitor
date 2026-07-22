"""
Generates fake credit card transactions.

Most transactions look "normal" - typical amounts for a given merchant
category, during typical hours. A small fraction are deliberately made to
look unusual (large amount, odd hour) to simulate real anomalies.
"""

import random
import uuid
from datetime import datetime, timedelta, timezone

MERCHANT_CATEGORIES = [
    "groceries", "restaurants", "gas", "electronics",
    "travel", "entertainment", "utilities", "clothing",
]

# Typical spending range per category, used to generate realistic amounts
NORMAL_AMOUNT_RANGE = {
    "groceries": (10, 150),
    "restaurants": (8, 90),
    "gas": (20, 80),
    "electronics": (30, 500),
    "travel": (50, 800),
    "entertainment": (10, 120),
    "utilities": (40, 250),
    "clothing": (15, 200),
}


def _random_timestamp(hour_range=(6, 23)):
    # Random timestamp within the last 24 hours, biased to normal waking hours
    now = datetime.now(timezone.utc)
    hour = random.randint(*hour_range)
    minute = random.randint(0, 59)
    return (now - timedelta(days=random.randint(0, 1))).replace(
        hour=hour, minute=minute, second=random.randint(0, 59)
    )


def generate_normal_transaction():
    """A transaction that looks like typical customer spending."""
    category = random.choice(MERCHANT_CATEGORIES)
    low, high = NORMAL_AMOUNT_RANGE[category]
    return {
        "transaction_id": str(uuid.uuid4()),
        "timestamp": _random_timestamp().isoformat(),
        "amount": round(random.uniform(low, high), 2),
        "merchant_category": category,
        "is_seed_anomaly": False,  # ground truth, for training/testing only
    }


def generate_anomalous_transaction():
    """A transaction deliberately shaped to look unusual."""
    category = random.choice(MERCHANT_CATEGORIES)
    low, high = NORMAL_AMOUNT_RANGE[category]
    # way-too-large amount, or a strange hour, or both.
    # 40% large amount, 30% odd hour, 30% both
    r = random.random()  # draw once, compare against thresholds
    if r < 0.4:
        amount = round(high * random.uniform(4, 10), 2)  # way too large
        timestamp = _random_timestamp()
    elif r < 0.7:
        amount = round(high * random.uniform(0.8, 1.5), 2)  # slightly large, not crazy
        timestamp = _random_timestamp(hour_range=(1, 4))  # odd hour
    else:
        amount = round(high * random.uniform(1.6, 3.9), 2)  # large AND odd hour
        timestamp = _random_timestamp(hour_range=(1, 4))
    return {
        "transaction_id": str(uuid.uuid4()),
        "timestamp": timestamp.isoformat(),
        "amount": amount,
        "merchant_category": category,
        "is_seed_anomaly": True,
    }


def generate_transaction(anomaly_rate=0.05):
    """Generate one transaction; anomalous with probability `anomaly_rate`."""
    if random.random() < anomaly_rate:
        return generate_anomalous_transaction()
    return generate_normal_transaction()


def generate_batch(n, anomaly_rate=0.05):
    """Generate a list of n transactions."""
    return [generate_transaction(anomaly_rate) for _ in range(n)]


if __name__ == "__main__":
    # Quick sanity check when running this file directly
    for txn in generate_batch(5, anomaly_rate=0.4):
        print(txn)
