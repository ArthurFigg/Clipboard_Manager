from db import history_repo


# --- salvar ---

def test_salvar_retorna_id_inteiro(conn_memoria):
    id = history_repo.salvar("conteúdo", "text", conn=conn_memoria)
    assert isinstance(id, int)
    assert id > 0


def test_salvar_persiste_conteudo(conn_memoria):
    history_repo.salvar("texto salvo", "text", conn=conn_memoria)
    itens = history_repo.listar(conn=conn_memoria)
    assert itens[0]["content"] == "texto salvo"


def test_salvar_persiste_categoria(conn_memoria):
    history_repo.salvar("https://example.com", "link", conn=conn_memoria)
    itens = history_repo.listar(conn=conn_memoria)
    assert itens[0]["category"] == "link"


def test_salvar_preenche_copied_at(conn_memoria):
    history_repo.salvar("conteúdo", "text", conn=conn_memoria)
    itens = history_repo.listar(conn=conn_memoria)
    assert itens[0]["copied_at"]


# --- listar ---

def test_listar_retorna_vazio_sem_itens(conn_memoria):
    assert history_repo.listar(conn=conn_memoria) == []


def test_listar_mais_recente_primeiro(conn_memoria):
    history_repo.salvar("primeiro", "text", conn=conn_memoria)
    history_repo.salvar("segundo", "text", conn=conn_memoria)
    itens = history_repo.listar(conn=conn_memoria)
    assert itens[0]["content"] == "segundo"
    assert itens[1]["content"] == "primeiro"


def test_listar_filtra_por_categoria(conn_memoria):
    history_repo.salvar("https://site.com", "link", conn=conn_memoria)
    history_repo.salvar("texto simples", "text", conn=conn_memoria)
    itens = history_repo.listar(categoria="link", conn=conn_memoria)
    assert len(itens) == 1
    assert itens[0]["category"] == "link"


def test_listar_filtra_por_busca(conn_memoria):
    history_repo.salvar("python é legal", "text", conn=conn_memoria)
    history_repo.salvar("java também", "text", conn=conn_memoria)
    itens = history_repo.listar(busca="python", conn=conn_memoria)
    assert len(itens) == 1
    assert "python" in itens[0]["content"]


def test_listar_busca_sem_match_retorna_vazio(conn_memoria):
    history_repo.salvar("texto qualquer", "text", conn=conn_memoria)
    assert history_repo.listar(busca="inexistente", conn=conn_memoria) == []


def test_listar_combina_categoria_e_busca(conn_memoria):
    history_repo.salvar("https://python.org", "link", conn=conn_memoria)
    history_repo.salvar("https://java.com", "link", conn=conn_memoria)
    history_repo.salvar("python como texto", "text", conn=conn_memoria)
    itens = history_repo.listar(categoria="link", busca="python", conn=conn_memoria)
    assert len(itens) == 1
    assert itens[0]["content"] == "https://python.org"


def test_listar_respeita_limite(conn_memoria):
    for i in range(10):
        history_repo.salvar(f"item {i}", "text", conn=conn_memoria)
    assert len(history_repo.listar(limite=3, conn=conn_memoria)) == 3


def test_listar_respeita_offset(conn_memoria):
    for i in range(5):
        history_repo.salvar(f"item {i}", "text", conn=conn_memoria)
    # offset=2 pula os 2 mais recentes (item 4, item 3)
    itens = history_repo.listar(limite=10, offset=2, conn=conn_memoria)
    assert len(itens) == 3
    assert itens[0]["content"] == "item 2"


# --- deletar ---

def test_deletar_remove_item(conn_memoria):
    id = history_repo.salvar("a deletar", "text", conn=conn_memoria)
    history_repo.deletar(id, conn=conn_memoria)
    itens = history_repo.listar(conn=conn_memoria)
    assert all(item["id"] != id for item in itens)


def test_deletar_id_inexistente_nao_levanta_excecao(conn_memoria):
    history_repo.deletar(9999, conn=conn_memoria)


# --- limpar ---

def test_limpar_remove_todos_os_itens(conn_memoria):
    history_repo.salvar("a", "text", conn=conn_memoria)
    history_repo.salvar("b", "text", conn=conn_memoria)
    history_repo.limpar(conn=conn_memoria)
    assert history_repo.listar(conn=conn_memoria) == []


def test_limpar_tabela_vazia_nao_levanta_excecao(conn_memoria):
    history_repo.limpar(conn=conn_memoria)


# --- limite de histórico ---

def test_limite_historico_remove_mais_antigos(conn_memoria):
    # insere 6 itens com limite de 5 — o mais antigo deve ser removido
    for i in range(6):
        history_repo.salvar(f"item {i}", "text", conn=conn_memoria, limite_historico=5)
    itens = history_repo.listar(limite=10, conn=conn_memoria)
    conteudos = [item["content"] for item in itens]
    assert len(itens) == 5
    assert "item 0" not in conteudos
    assert "item 5" in conteudos


def test_limite_historico_preserva_os_mais_recentes(conn_memoria):
    for i in range(5):
        history_repo.salvar(f"item {i}", "text", conn=conn_memoria, limite_historico=3)
    itens = history_repo.listar(limite=10, conn=conn_memoria)
    conteudos = [item["content"] for item in itens]
    assert conteudos == ["item 4", "item 3", "item 2"]
