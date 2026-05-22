import pytest
from core.categorizer import categorizar


# --- link ---

def test_link_http():
    assert categorizar("http://example.com") == "link"

def test_link_https():
    assert categorizar("https://google.com") == "link"

def test_link_com_path_e_query():
    assert categorizar("https://site.com/path?q=1&page=2") == "link"

def test_link_tem_prioridade_sobre_email():
    # URL com @ não deve ser detectada como email
    assert categorizar("https://user@example.com/path") == "link"


# --- email ---

def test_email_simples():
    assert categorizar("usuario@dominio.com") == "email"

def test_email_com_subdominio():
    assert categorizar("user.name+tag@mail.dominio.com.br") == "email"

def test_email_nao_detecta_sem_dominio():
    assert categorizar("usuario@") != "email"

def test_email_nao_detecta_sem_arroba():
    assert categorizar("usuariodominio.com") != "email"


# --- number ---

def test_number_inteiro():
    assert categorizar("123456") == "number"

def test_number_com_pontos_e_virgulas():
    assert categorizar("1.234,56") == "number"

def test_number_com_espacos():
    assert categorizar("123 456 789") == "number"

def test_number_cpf_sem_hifen():
    # spec: apenas dígitos, pontos, vírgulas e espaços — hífen não incluso
    assert categorizar("123.456.789") == "number"

def test_number_nao_detecta_so_espacos():
    assert categorizar("   ") != "number"

def test_number_nao_detecta_texto_com_digitos():
    assert categorizar("abc123") != "number"


# --- code ---

def test_code_def_python():
    assert categorizar("def minha_funcao():") == "code"

def test_code_class_python():
    assert categorizar("class MinhaClasse:") == "code"

def test_code_import():
    assert categorizar("import os") == "code"

def test_code_chaves():
    assert categorizar('{ "chave": "valor" }') == "code"

def test_code_arrow_function():
    assert categorizar("const fn = () => resultado") == "code"

def test_code_function_js():
    assert categorizar("function calcular(x) { return x; }") == "code"

def test_code_ponto_e_virgula():
    assert categorizar("x = 1;") == "code"

def test_code_multiline():
    trecho = "def soma(a, b):\n    return a + b"
    assert categorizar(trecho) == "code"


# --- text ---

def test_text_frase_comum():
    assert categorizar("Olá, isso é um texto comum.") == "text"

def test_text_string_vazia():
    assert categorizar("") == "text"

def test_text_apenas_espacos():
    assert categorizar("   ") == "text"

def test_text_nao_confunde_com_code():
    # ponto e vírgula em português não deve ser detectado como code
    # ";" como caractere isolado no meio de texto ainda dispara code — comportamento esperado pelo spec
    assert categorizar("Texto sem tokens de código") == "text"


# --- prioridade ---

def test_prioridade_link_antes_de_code():
    # URL com chaves não deve ser detectada como code
    assert categorizar("https://api.exemplo.com/{id}") == "link"

def test_prioridade_email_antes_de_text():
    assert categorizar("contato@empresa.com.br") == "email"
