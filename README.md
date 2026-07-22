# transaction-monitor

## Phase 1: Data Generation & Anomaly Detection

## Overview
This phase focuses on generating historical transaction data and training an anomaly detection model. At this stage, the project runs entirely in Python with **no Kafka or streaming infrastructure**.

## Project Structure

```text
.
├── transaction_generator.py      # Generates synthetic transaction data
├── historical_transactions.csv   # Historical transaction dataset
├── train_model.py                # Trains the Isolation Forest model
├── model.py                      # Loads the trained model for predictions
└── model.pkl                     # Trained model (generated after training)
```

## Isolation Forest

Isolation Forest is an **unsupervised anomaly detection** algorithm that identifies unusual transactions by randomly isolating data points.

- Builds multiple random decision trees.
- Randomly selects a feature and a split value at each node.
- Anomalous transactions are isolated in **fewer splits** because they are rare and differ from normal data.
- Normal transactions require **more splits** since they are surrounded by similar observations.

The model predicts:
- `1` → Normal transaction
- `-1` → Anomalous transaction

## Running

### 1. Generate historical data

```bash
python transaction_generator.py
```

This creates `historical_transactions.csv`.

### 2. Train the model

```bash
python train_model.py
```

This generates the trained model:

```text
model.pkl
```

### 3. Test predictions

```bash
python model.py
```

## Output

After completing this phase, you will have:
- A synthetic historical transaction dataset.
- A trained Isolation Forest model (`model.pkl`).
- A local anomaly detection pipeline capable of classifying transactions as **normal** or **anomalous**.