import json
from typing import Any, Literal

# Suporta dict e sqlite3.Row — ambos têm keys() e acesso por []
Item = dict[str, Any]

FormatoExportacao = Literal["txt", "json", "md"]

_CABECALHOS = {
    "id": "ID",
    "content": "Conteúdo",
    "category": "Categoria",
    "copied_at": "Copiado em",
    "name": "Nome",
    "created_at": "Criado em",
}


def exportar_txt(itens: list[Item]) -> str:
    """Um conteúdo por linha."""
    return "\n".join(str(item["content"]) for item in itens)


def exportar_json(itens: list[Item]) -> str:
    """Array JSON com todos os campos de cada item."""
    # dict() converte sqlite3.Row para dict serializável
    dados = [dict(item) for item in itens]
    return json.dumps(dados, ensure_ascii=False, indent=2)


def exportar_md(itens: list[Item]) -> str:
    """Tabela Markdown com cabeçalhos legíveis."""
    if not itens:
        return ""

    colunas = list(dict(itens[0]).keys())
    cabecalhos = [_CABECALHOS.get(col, col) for col in colunas]

    linha_cabecalho = "| " + " | ".join(cabecalhos) + " |"
    linha_separador = "| " + " | ".join("---" for _ in colunas) + " |"

    linhas_dados = []
    for item in itens:
        valores = [str(dict(item).get(col, "")) for col in colunas]
        linhas_dados.append("| " + " | ".join(valores) + " |")

    return "\n".join([linha_cabecalho, linha_separador] + linhas_dados)


_EXPORTADORES: dict[str, Any] = {
    "txt": exportar_txt,
    "json": exportar_json,
    "md": exportar_md,
}


def exportar(itens: list[Item], formato: FormatoExportacao) -> str:
    """Exporta lista de itens no formato solicitado."""
    if formato not in _EXPORTADORES:
        raise ValueError(
            f"Formato não suportado: {formato!r}. Formatos válidos: {list(_EXPORTADORES)}"
        )
    return _EXPORTADORES[formato](itens)
