from __future__ import annotations

import json
import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
  account_id TEXT PRIMARY KEY, name TEXT NOT NULL, arr INTEGER NOT NULL,
  health_score INTEGER NOT NULL CHECK (health_score BETWEEN 0 AND 100)
);
CREATE TABLE IF NOT EXISTS interactions (
  id INTEGER PRIMARY KEY, account_id TEXT NOT NULL, occurred_at TEXT NOT NULL,
  channel TEXT NOT NULL, content TEXT NOT NULL,
  FOREIGN KEY(account_id) REFERENCES customers(account_id)
);
CREATE VIRTUAL TABLE IF NOT EXISTS interaction_search USING fts5(
  content, account_id UNINDEXED, interaction_id UNINDEXED
);
CREATE TABLE IF NOT EXISTS workflow_runs (
  run_id TEXT PRIMARY KEY, account_id TEXT NOT NULL, status TEXT NOT NULL,
  state_json TEXT NOT NULL, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


class Store:
    def __init__(self, path: str | Path):
        self.path = str(path)
        self.connection = sqlite3.connect(self.path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys=ON")

    def initialize(self) -> None:
        self.connection.executescript(SCHEMA)
        self.connection.commit()

    def seed(self) -> None:
        customers = [
            ("ACME-001", "Acme Health", 420000, 31),
            ("NOVA-002", "Nova Retail", 180000, 78),
        ]
        interactions = [
            (1, "ACME-001", "2026-07-18", "support", "Third export outage this month; finance cannot close reports."),
            (2, "ACME-001", "2026-07-24", "email", "Champion says renewal is at risk unless reliability improves before Q4."),
            (3, "ACME-001", "2026-07-30", "meeting", "Customer requested an executive recovery plan and weekly status updates."),
            (4, "NOVA-002", "2026-07-22", "support", "Asked how to enable the new dashboard filters; issue resolved in one call."),
        ]
        self.connection.executemany("INSERT OR IGNORE INTO customers VALUES (?, ?, ?, ?)", customers)
        self.connection.executemany("INSERT OR IGNORE INTO interactions VALUES (?, ?, ?, ?, ?)", interactions)
        for row in interactions:
            self.connection.execute(
                "INSERT INTO interaction_search(content, account_id, interaction_id) "
                "SELECT ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM interaction_search WHERE interaction_id=?)",
                (row[4], row[1], row[0], row[0]),
            )
        self.connection.commit()

    def customer(self, account_id: str) -> dict | None:
        row = self.connection.execute(
            "SELECT account_id, name, arr, health_score FROM customers WHERE account_id=?", (account_id,)
        ).fetchone()
        return dict(row) if row else None

    def search(self, account_id: str, query: str, limit: int = 3) -> list[dict]:
        if not 1 <= limit <= 10:
            raise ValueError("limit must be between 1 and 10")
        terms = [t.lower() for t in query.split() if t.isalnum() and len(t) > 2]
        match = " OR ".join(dict.fromkeys(terms)) or "risk"
        rows = self.connection.execute(
            """SELECT i.id interaction_id, i.occurred_at, i.channel, i.content,
                      bm25(interaction_search) score
                 FROM interaction_search JOIN interactions i
                   ON i.id=interaction_search.interaction_id
                WHERE interaction_search MATCH ? AND interaction_search.account_id=?
                ORDER BY score, i.id LIMIT ?""",
            (match, account_id, limit),
        ).fetchall()
        if not rows:
            rows = self.connection.execute(
                "SELECT id interaction_id, occurred_at, channel, content, 100.0 score "
                "FROM interactions WHERE account_id=? ORDER BY occurred_at DESC LIMIT ?",
                (account_id, limit),
            ).fetchall()
        return [dict(r) for r in rows]

    def save_run(self, run_id: str, account_id: str, status: str, state: dict) -> None:
        payload = json.dumps(state, sort_keys=True)
        self.connection.execute(
            """INSERT INTO workflow_runs(run_id, account_id, status, state_json) VALUES (?, ?, ?, ?)
               ON CONFLICT(run_id) DO UPDATE SET status=excluded.status,
                 state_json=excluded.state_json, updated_at=CURRENT_TIMESTAMP""",
            (run_id, account_id, status, payload),
        )
        self.connection.commit()

    def load_run(self, run_id: str) -> dict | None:
        row = self.connection.execute(
            "SELECT run_id, account_id, status, state_json FROM workflow_runs WHERE run_id=?", (run_id,)
        ).fetchone()
        if not row:
            return None
        result = dict(row)
        result["state"] = json.loads(result.pop("state_json"))
        return result
