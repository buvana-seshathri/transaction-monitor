"""
Consumer: reads transactions off Kafka as they arrive, scores each one
with the pretrained anomaly model, and saves the result to SQLite.
This is the real-time part of the system, that consumes real-world events, judges and stores them.
"""

import json

from kafka import KafkaConsumer

import config
import database
import model


def main():
    database.init_db()
    trained_model, encoder = model.load()

    consumer = KafkaConsumer(
        config.KAFKA_TOPIC,
        bootstrap_servers=config.KAFKA_BROKER,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",  # only process new messages, not old ones
    )
    print(f"Listening on topic '{config.KAFKA_TOPIC}'. Ctrl+C to stop.")

    try:
        for message in consumer:
            txn = message.value
            is_anomaly, score = model.score(txn, trained_model, encoder)
            database.insert_transaction(txn, is_anomaly, score)

            flag = "ANOMALY" if is_anomaly else "normal"
            print(f"[{flag}] ${txn['amount']:.2f} {txn['merchant_category']} (score={score})")
    except KeyboardInterrupt:
        print("\nStopping consumer.")
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
