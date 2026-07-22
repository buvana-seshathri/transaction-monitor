"""
Anomaly detection model.

Wraps scikit-learn's IsolationForest, which learns what "normal" transactions
look like from historical data, then scores new transactions by how much
they deviate from that pattern. No labels are needed for training - it
learns the shape of normal data and flags outliers.
"""

from datetime import datetime

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import OneHotEncoder

from transaction_generator import MERCHANT_CATEGORIES

MODEL_PATH = "model.pkl"
ENCODER_PATH = "encoder.pkl"


def _extract_features(transactions):
    """Turn a list of transaction dicts into a numeric feature DataFrame."""
    df = pd.DataFrame(transactions)
    df["hour"] = df["timestamp"].apply(lambda t: datetime.fromisoformat(t).hour)
    return df[["amount", "hour", "merchant_category"]]


def train(transactions, contamination=0.05):
    """
    Train the anomaly model on a list of transaction dicts.
    Returns (model, encoder) - both need to be saved for later scoring.
    """
    features = _extract_features(transactions)

    encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore") # sparse_output: stores all values instead of just non-zero values
    encoder.fit(features[["merchant_category"]])

    X = _build_matrix(features, encoder)

    model = IsolationForest(contamination=contamination, random_state=42)
    model.fit(X)

    return model, encoder


def _build_matrix(features, encoder):
    """Combine numeric columns + one-hot encoded category into a matrix."""
    category_encoded = encoder.transform(features[["merchant_category"]])
    numeric = features[["amount", "hour"]].to_numpy()
    return pd.concat(
        [pd.DataFrame(numeric), pd.DataFrame(category_encoded)], axis=1
    ).to_numpy()


def save(model, encoder):
    joblib.dump(model, MODEL_PATH)
    joblib.dump(encoder, ENCODER_PATH)


def load():
    model = joblib.load(MODEL_PATH)
    encoder = joblib.load(ENCODER_PATH)
    return model, encoder


def score(transaction, model, encoder):
    """
    Score a single transaction dict.
    Returns (is_anomaly: bool, anomaly_score: float).
    Lower score = more anomalous.
    """
    features = _extract_features([transaction])
    X = _build_matrix(features, encoder)

    prediction = model.predict(X)[0]  # -1 = anomaly, 1 = normal
    raw_score = model.decision_function(X)[0]

    return prediction == -1, round(float(raw_score), 4)
