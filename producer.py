"""
Producer: continuously generates fake transactions and publishes them to Kafka.
This is the fake simulation of real-time real-world card swipe events.
"""

import json
import time

from kafka import KafkaProducer

import config
from transaction_generator import generate_transaction


def main():
    producer = KafkaProducer(
        bootstrap_servers=config.KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    print(f"Producing to topic '{config.KAFKA_TOPIC}' every {config.PRODUCE_INTERVAL_SECONDS}s. Ctrl+C to stop.")

    try:
        while True:
            txn = generate_transaction(anomaly_rate=config.ANOMALY_RATE)
            producer.send(config.KAFKA_TOPIC, value=txn)
            print(f"Sent: ${txn['amount']:.2f} {txn['merchant_category']}"
                  f"{'  <-- seeded anomaly' if txn['is_seed_anomaly'] else ''}")
            time.sleep(config.PRODUCE_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nStopping producer.")
    finally:
        producer.flush()
        producer.close()


if __name__ == "__main__":
    main()
