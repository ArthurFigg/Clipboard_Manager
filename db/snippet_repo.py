import sqlite3
from datetime import datetime

from db.connection import obter_conexao


def salvar(
    name: str,
    content: str,
    conn: sqlite3.Connection | None = None,
) -> int:
    """Insere novo snippet e retorna o id gerado."""
    _conn = conn or obter_conexao()
    agora = datetime.now().isoformat()

    cursor = _conn.execute(
        "INSERT INTO snippets (name, content, created_at) VALUES (?, ?, ?)",
        (name, content, agora),
    )
    _conn.commit()
    return cursor.lastrowid  # type: ignore[return-value]


def listar(conn: sqlite3.Connection | None = None) -> list[sqlite3.Row]:
    """Retorna todos os snippets, mais recentes primeiro."""
    _conn = conn or obter_conexao()
    cursor = _conn.execute("SELECT * FROM snippets ORDER BY id DESC")
    return cursor.fetchall()


def atualizar(
    id: int,
    name: str,
    content: str,
    conn: sqlite3.Connection | None = None,
) -> None:
    """Atualiza nome e conteúdo de um snippet existente."""
    _conn = conn or obter_conexao()
    _conn.execute(
        "UPDATE snippets SET name = ?, content = ? WHERE id = ?",
        (name, content, id),
    )
    _conn.commit()


def deletar(id: int, conn: sqlite3.Connection | None = None) -> None:
    """Remove snippet pelo id."""
    _conn = conn or obter_conexao()
    _conn.execute("DELETE FROM snippets WHERE id = ?", (id,))
    _conn.commit()
