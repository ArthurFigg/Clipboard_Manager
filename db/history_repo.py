import sqlite3
from datetime import datetime

from db.connection import obter_conexao

LIMITE_HISTORICO = 500


def salvar(
    content: str,
    category: str,
    conn: sqlite3.Connection | None = None,
    limite_historico: int = LIMITE_HISTORICO,
) -> int:
    """Insere item no histórico e mantém o limite máximo de entradas."""
    _conn = conn or obter_conexao()
    agora = datetime.now().isoformat()

    cursor = _conn.execute(
        "INSERT INTO history (content, category, copied_at) VALUES (?, ?, ?)",
        (content, category, agora),
    )
    novo_id = cursor.lastrowid

    # Mantém apenas os N mais recentes (por id DESC); remove os excedentes
    _conn.execute(
        """
        DELETE FROM history
        WHERE id NOT IN (
            SELECT id FROM history ORDER BY id DESC LIMIT ?
        )
        """,
        (limite_historico,),
    )

    _conn.commit()
    return novo_id  # type: ignore[return-value]  # lastrowid é sempre int após INSERT


def listar(
    limite: int = 50,
    offset: int = 0,
    categoria: str | None = None,
    busca: str | None = None,
    conn: sqlite3.Connection | None = None,
) -> list[sqlite3.Row]:
    """Retorna itens do histórico, mais recentes primeiro, com filtros opcionais."""
    _conn = conn or obter_conexao()

    clausulas: list[str] = []
    parametros: list = []

    if categoria:
        clausulas.append("category = ?")
        parametros.append(categoria)

    if busca:
        clausulas.append("content LIKE ?")
        parametros.append(f"%{busca}%")

    where = f"WHERE {' AND '.join(clausulas)}" if clausulas else ""
    parametros.extend([limite, offset])

    cursor = _conn.execute(
        f"SELECT * FROM history {where} ORDER BY id DESC LIMIT ? OFFSET ?",
        parametros,
    )
    return cursor.fetchall()


def deletar(id: int, conn: sqlite3.Connection | None = None) -> None:
    """Remove item do histórico pelo id."""
    _conn = conn or obter_conexao()
    _conn.execute("DELETE FROM history WHERE id = ?", (id,))
    _conn.commit()


def limpar(conn: sqlite3.Connection | None = None) -> None:
    """Remove todos os itens do histórico."""
    _conn = conn or obter_conexao()
    _conn.execute("DELETE FROM history")
    _conn.commit()
