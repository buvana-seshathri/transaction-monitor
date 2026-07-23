// Polls the FastAPI backend and refreshes the table.
// No frameworks - just fetch() and plain DOM updates.

const API_BASE = "http://localhost:8000";
const POLL_INTERVAL_MS = 3000;

async function fetchStats() {
  const res = await fetch(`${API_BASE}/stats`);
  return res.json();
}

async function fetchTransactions() {
  const res = await fetch(`${API_BASE}/transactions?limit=25`);
  return res.json();
}

function renderStats(stats) {
  document.getElementById("stat-total").textContent = `Total: ${stats.total}`;
  document.getElementById("stat-anomalies").textContent = `Anomalies: ${stats.anomalies}`;
  document.getElementById("stat-rate").textContent =
    `Rate: ${(stats.anomaly_rate * 100).toFixed(1)}%`;
}

function renderTransactions(transactions) {
  const tbody = document.getElementById("transaction-rows");
  tbody.innerHTML = ""; // simplest approach - full re-render each poll

  for (const txn of transactions) {
    const row = document.createElement("tr");
    row.classList.add(txn.is_anomaly ? "anomaly" : "normal");

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

async function refresh() {
  try {
    const [stats, transactions] = await Promise.all([fetchStats(), fetchTransactions()]);
    renderStats(stats);
    renderTransactions(transactions);
  } catch (err) {
    console.error("Failed to fetch from API - is it running on :8000?", err);
  }
}

refresh();
setInterval(refresh, POLL_INTERVAL_MS);
