import json
import pytest
from export.exporter import exportar, exportar_json, exportar_md, exportar_txt

# Fixtures reutilizáveis

ITENS_HISTORY = [
    {"id": 1, "content": "https://python.org", "category": "link", "copied_at": "2024-01-01T10:00:00"},
    {"id": 2, "content": "usuario@email.com", "category": "email", "copied_at": "2024-01-01T11:00:00"},
    {"id": 3, "content": "texto simples", "category": "text", "copied_at": "2024-01-01T12:00:00"},
]

ITENS_SNIPPETS = [
    {"id": 1, "name": "saudação", "content": "Olá, mundo!", "created_at": "2024-01-01T09:00:00"},
]


# ---------------------------------------------------------------------------
# exportar_txt
# ---------------------------------------------------------------------------

def test_txt_retorna_conteudos_por_linha():
    resultado = exportar_txt(ITENS_HISTORY)
    linhas = resultado.split("\n")
    assert linhas[0] == "https://python.org"
    assert linhas[1] == "usuario@email.com"
    assert linhas[2] == "texto simples"


def test_txt_lista_vazia_retorna_string_vazia():
    assert exportar_txt([]) == ""


def test_txt_item_unico_sem_quebra_de_linha():
    resultado = exportar_txt([{"content": "único"}])
    assert resultado == "único"
    assert "\n" not in resultado


def test_txt_tres_itens_tem_duas_quebras_de_linha():
    resultado = exportar_txt(ITENS_HISTORY)
    assert resultado.count("\n") == 2


# ---------------------------------------------------------------------------
# exportar_json
# ---------------------------------------------------------------------------

def test_json_retorna_string_valida():
    resultado = exportar_json(ITENS_HISTORY)
    dados = json.loads(resultado)  # não levanta exceção
    assert isinstance(dados, list)


def test_json_lista_vazia_retorna_array_vazio():
    resultado = exportar_json([])
    assert json.loads(resultado) == []


def test_json_preserva_todos_os_campos():
    resultado = exportar_json([ITENS_HISTORY[0]])
    dados = json.loads(resultado)
    assert dados[0]["id"] == 1
    assert dados[0]["content"] == "https://python.org"
    assert dados[0]["category"] == "link"
    assert dados[0]["copied_at"] == "2024-01-01T10:00:00"


def test_json_preserva_quantidade_de_itens():
    resultado = exportar_json(ITENS_HISTORY)
    dados = json.loads(resultado)
    assert len(dados) == 3


def test_json_nao_escapa_caracteres_especiais():
    item = [{"content": "café, ação, naïve"}]
    resultado = exportar_json(item)
    assert "café" in resultado
    assert "ação" in resultado


def test_json_funciona_com_snippets():
    resultado = exportar_json(ITENS_SNIPPETS)
    dados = json.loads(resultado)
    assert dados[0]["name"] == "saudação"


# ---------------------------------------------------------------------------
# exportar_md
# ---------------------------------------------------------------------------

def test_md_lista_vazia_retorna_string_vazia():
    assert exportar_md([]) == ""


def test_md_tem_linha_de_cabecalho():
    resultado = exportar_md(ITENS_HISTORY)
    primeira_linha = resultado.split("\n")[0]
    assert primeira_linha.startswith("|")
    assert primeira_linha.endswith("|")


def test_md_cabecalhos_sao_legíveis():
    resultado = exportar_md(ITENS_HISTORY)
    primeira_linha = resultado.split("\n")[0]
    assert "Conteúdo" in primeira_linha
    assert "Categoria" in primeira_linha


def test_md_tem_linha_separadora():
    resultado = exportar_md(ITENS_HISTORY)
    segunda_linha = resultado.split("\n")[1]
    assert "---" in segunda_linha


def test_md_tem_linha_por_item():
    resultado = exportar_md(ITENS_HISTORY)
    linhas = resultado.split("\n")
    # cabeçalho + separador + N itens
    assert len(linhas) == 2 + len(ITENS_HISTORY)


def test_md_conteudo_aparece_nas_linhas_de_dados():
    resultado = exportar_md(ITENS_HISTORY)
    assert "https://python.org" in resultado
    assert "usuario@email.com" in resultado


def test_md_funciona_com_snippets():
    resultado = exportar_md(ITENS_SNIPPETS)
    assert "Nome" in resultado
    assert "saudação" in resultado


# ---------------------------------------------------------------------------
# exportar (dispatcher)
# ---------------------------------------------------------------------------

def test_exportar_despacha_para_txt():
    resultado = exportar(ITENS_HISTORY, "txt")
    assert "https://python.org" in resultado
    assert resultado.count("\n") == 2


def test_exportar_despacha_para_json():
    resultado = exportar(ITENS_HISTORY, "json")
    dados = json.loads(resultado)
    assert len(dados) == 3


def test_exportar_despacha_para_md():
    resultado = exportar(ITENS_HISTORY, "md")
    assert "Conteúdo" in resultado
    assert "---" in resultado


def test_exportar_formato_invalido_levanta_value_error():
    with pytest.raises(ValueError, match="Formato não suportado"):
        exportar(ITENS_HISTORY, "csv")  # type: ignore
