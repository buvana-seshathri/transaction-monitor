"""
Central place for settings shared across producer.py and consumer.py.
Change these here instead of hunting through multiple files.
"""

KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "transactions"

PRODUCE_INTERVAL_SECONDS = 1  # how often the producer sends a new transaction
ANOMALY_RATE = 0.08  # slightly higher than training data, so the demo has more to show
