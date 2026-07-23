"""
FastAPI app that serves scored transactions from the database.
This is the layer between the SQLite data and the dashboard - just two
read endpoints, no auth, no write endpoints (the consumer owns writing).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import database

app = FastAPI(title="Transaction Anomaly Detection API")

# Allows the dashboard (served separately, e.g. opened as a local file
# or a different port) to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/transactions")
def list_transactions(limit: int = 50):
    """Most recent transactions, newest first."""
    return database.get_recent(limit=limit)


@app.get("/anomalies")
def list_anomalies(limit: int = 50):
    """Most recent flagged transactions only."""
    return database.get_anomalies(limit=limit)


@app.get("/stats")
def stats():
    """Quick summary counts for the dashboard header."""
    recent = database.get_recent(limit=1000)
    anomalies = [t for t in recent if t["is_anomaly"]]
    return {
        "total": len(recent),
        "anomalies": len(anomalies),
        "anomaly_rate": round(len(anomalies) / len(recent), 4) if recent else 0,
    }
