"""Tiny analytics SQLite store for read-only text-to-SQL exercises."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from app.sql_guard import enforce_timeout_budget, reject_dangerous_sql

DDL: dict[str, str] = {
    "users": (
        "CREATE TABLE users ("
        "id INTEGER PRIMARY KEY, name TEXT NOT NULL, created_at TEXT NOT NULL)"
    ),
    "orders": (
        "CREATE TABLE orders ("
        "id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, amount REAL NOT NULL, "
        "FOREIGN KEY(user_id) REFERENCES users(id))"
    ),
}

SEED_USERS = [
    (1, "Ada", "2026-01-10"),
    (2, "Grace", "2025-11-02"),
    (3, "Linus", "2026-03-18"),
]
SEED_ORDERS = [
    (1, 1, 120.0),
    (2, 1, 80.5),
    (3, 2, 40.0),
    (4, 3, 220.0),
]


class AnalyticsStore:
    def __init__(self, path: str | Path):
        self.path = str(path)
        self.connection = sqlite3.connect(self.path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row

    def initialize(self) -> None:
        for ddl in DDL.values():
            self.connection.execute(ddl)
        self.connection.commit()

    def seed(self) -> None:
        self.connection.executemany("INSERT OR IGNORE INTO users VALUES (?, ?, ?)", SEED_USERS)
        self.connection.executemany("INSERT OR IGNORE INTO orders VALUES (?, ?, ?)", SEED_ORDERS)
        self.connection.commit()

    def schema_for(self, table_name: str) -> str:
        key = table_name.strip().lower()
        if key not in DDL:
            raise ValueError(f"unknown table: {table_name}")
        return DDL[key]

    def list_tables(self) -> list[str]:
        return sorted(DDL)

    def execute_readonly(self, sql: str, timeout_seconds: float = 5.0) -> list[dict]:
        enforce_timeout_budget(timeout_seconds)
        safe = reject_dangerous_sql(sql)
        self.connection.execute(f"PRAGMA busy_timeout={int(timeout_seconds * 1000)}")
        rows = self.connection.execute(safe).fetchall()
        return [dict(r) for r in rows]
