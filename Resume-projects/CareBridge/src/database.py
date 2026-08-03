from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "carebridge.db"
SCHEMA_PATH = ROOT / "sql" / "schema.sql"
SEED_PATH = ROOT / "sql" / "seed.sql"


def connect(path: Path = DB_PATH) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def initialize(path: Path = DB_PATH) -> None:
    with connect(path) as connection:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        count = connection.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
        if count == 0:
            connection.executescript(SEED_PATH.read_text(encoding="utf-8"))
        # Migrate labels created by earlier student-MVP versions.
        connection.execute("UPDATE documents SET title='Blood panel report' WHERE title='Synthetic blood panel'")
        connection.execute("UPDATE documents SET title='Insurance card' WHERE title='Demo insurance card'")
        connection.commit()


def query(sql: str, params: tuple = (), path: Path = DB_PATH) -> pd.DataFrame:
    with connect(path) as connection:
        return pd.read_sql_query(sql, connection, params=params)


def execute(sql: str, params: tuple = (), path: Path = DB_PATH) -> None:
    with connect(path) as connection:
        connection.execute(sql, params)
        connection.commit()
