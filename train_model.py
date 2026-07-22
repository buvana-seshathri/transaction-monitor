"""
One-time training script.

Generates a batch of historical transactions, saves them to CSV (so you can
inspect what the model learned from), trains the anomaly model, and saves
it to disk so consumer.py can load it later without retraining.
"""

import pandas as pd

import model
from transaction_generator import generate_batch

HISTORICAL_DATA_PATH = "historical_transactions.csv"
NUM_HISTORICAL_TRANSACTIONS = 5000
ANOMALY_RATE = 0.05  # 5% of historical data is seeded as anomalous


def main():
    print(f"Generating {NUM_HISTORICAL_TRANSACTIONS} historical transactions...")
    transactions = generate_batch(NUM_HISTORICAL_TRANSACTIONS, ANOMALY_RATE) # generate_batch returns list

    df = pd.DataFrame(transactions)
    df.to_csv(HISTORICAL_DATA_PATH, index=False) # index=False: tells pd not to save the index as a separate column
    print(f"Saved historical data to {HISTORICAL_DATA_PATH}")

    print("Training anomaly model...")
    trained_model, encoder = model.train(transactions, contamination=ANOMALY_RATE)
    model.save(trained_model, encoder)
    print(f"Saved model to {model.MODEL_PATH} and encoder to {model.ENCODER_PATH}")

    _evaluate(transactions, trained_model, encoder)


def _evaluate(transactions, trained_model, encoder):
    """Quick sanity check: how well did the model catch our seeded anomalies?"""
    correct = 0
    for txn in transactions:
        predicted_anomaly, _ = model.score(txn, trained_model, encoder)
        if predicted_anomaly == txn["is_seed_anomaly"]:
            correct += 1
    accuracy = correct / len(transactions)
    print(f"Model agreement with seeded anomaly labels: {accuracy:.1%}")
    print("(Not a real accuracy metric)")


if __name__ == "__main__":
    main()
