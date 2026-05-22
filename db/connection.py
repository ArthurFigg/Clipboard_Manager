import sqlite3
from pathlib import Path


def _caminho_banco() -> Path:
    base = Path.home() / "AppData" / "Local" / "ClipboardManager"
    base.mkdir(parents=True, exist_ok=True)
    return base / "data.db"


def obter_conexao() -> sqlite3.Connection:
    conn = sqlite3.connect(_caminho_banco(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_banco() -> None:
    with obter_conexao() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS history (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                content   TEXT    NOT NULL,
                category  TEXT    NOT NULL,
                copied_at TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS snippets (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                content    TEXT    NOT NULL,
                created_at TEXT    NOT NULL
            );
        """)
