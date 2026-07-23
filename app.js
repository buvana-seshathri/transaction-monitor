// Polls the FastAPI backend and refreshes the SOC-style dashboard.
// No frameworks - just fetch() and plain DOM updates.

const API_BASE = "http://localhost:8000";
const POLL_INTERVAL_MS = 3000;

// Tracks anomaly IDs we've already flashed, so each one only pulses once
// the first time it's seen - not on every subsequent poll.
const seenAnomalyIds = new Set();

async function fetchStats() {
  const res = await fetch(`${API_BASE}/stats`);
  return res.json();
}

async function fetchTransactions() {
  const res = await fetch(`${API_BASE}/transactions?limit=25`);
  return res.json();
}

function renderStats(stats) {
  document.getElementById("stat-total").textContent = stats.total;
  document.getElementById("stat-anomalies").textContent = stats.anomalies;
  document.getElementById("stat-rate").textContent =
    `${(stats.anomaly_rate * 100).toFixed(1)}%`;
}

function renderTransactions(transactions) {
  const tbody = document.getElementById("transaction-rows");
  tbody.innerHTML = ""; // simplest approach - full re-render each poll

  for (const txn of transactions) {
    const row = document.createElement("tr");
    row.classList.add(txn.is_anomaly ? "anomaly" : "normal");

    // Flash only the first time we see a given anomaly, not every poll.
    if (txn.is_anomaly && !seenAnomalyIds.has(txn.transaction_id)) {
      row.classList.add("flash");
      seenAnomalyIds.add(txn.transaction_id);
    }

    const time = new Date(txn.timestamp).toLocaleTimeString();
    row.innerHTML = `
      <td>${time}</td>
      <td>$${txn.amount.toFixed(2)}</td>
      <td>${txn.merchant_category}</td>
      <td>${txn.anomaly_score}</td>
      <td>${txn.is_anomaly ? "ANOMALY" : "normal"}</td>
    `;
    tbody.appendChild(row);
  }
}

function renderLastUpdated() {
  const now = new Date().toLocaleTimeString();
  document.getElementById("last-updated").textContent = `last update: ${now}`;
}

async function refresh() {
  try {
    const [stats, transactions] = await Promise.all([fetchStats(), fetchTransactions()]);
    renderStats(stats);
    renderTransactions(transactions);
    renderLastUpdated();
  } catch (err) {
    console.error("Failed to fetch from API - is it running on :8000?", err);
  }
}

refresh();
setInterval(refresh, POLL_INTERVAL_MS);
