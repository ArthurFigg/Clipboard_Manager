import sqlite3
import pytest


@pytest.fixture
def conn_memoria():
    """Conexão SQLite em memória com o schema completo. Isolada por teste."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE history (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            content   TEXT    NOT NULL,
            category  TEXT    NOT NULL,
            copied_at TEXT    NOT NULL
        );
        CREATE TABLE snippets (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
            content    TEXT    NOT NULL,
            created_at TEXT    NOT NULL
        );
    """)
    yield conn
    conn.close()
