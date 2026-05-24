from db import snippet_repo


# --- salvar ---

def test_salvar_retorna_id_inteiro(conn_memoria):
    id = snippet_repo.salvar("meu snippet", "conteúdo aqui", conn=conn_memoria)
    assert isinstance(id, int)
    assert id > 0


def test_salvar_persiste_nome(conn_memoria):
    snippet_repo.salvar("nome do snippet", "conteúdo", conn=conn_memoria)
    itens = snippet_repo.listar(conn=conn_memoria)
    assert itens[0]["name"] == "nome do snippet"


def test_salvar_persiste_conteudo(conn_memoria):
    snippet_repo.salvar("nome", "conteúdo do snippet", conn=conn_memoria)
    itens = snippet_repo.listar(conn=conn_memoria)
    assert itens[0]["content"] == "conteúdo do snippet"


def test_salvar_preenche_created_at(conn_memoria):
    snippet_repo.salvar("nome", "conteúdo", conn=conn_memoria)
    itens = snippet_repo.listar(conn=conn_memoria)
    assert itens[0]["created_at"]


# --- listar ---

def test_listar_retorna_vazio_sem_snippets(conn_memoria):
    assert snippet_repo.listar(conn=conn_memoria) == []


def test_listar_mais_recente_primeiro(conn_memoria):
    snippet_repo.salvar("primeiro", "a", conn=conn_memoria)
    snippet_repo.salvar("segundo", "b", conn=conn_memoria)
    itens = snippet_repo.listar(conn=conn_memoria)
    assert itens[0]["name"] == "segundo"
    assert itens[1]["name"] == "primeiro"


def test_listar_retorna_todos_os_snippets(conn_memoria):
    for i in range(5):
        snippet_repo.salvar(f"snippet {i}", f"conteúdo {i}", conn=conn_memoria)
    assert len(snippet_repo.listar(conn=conn_memoria)) == 5


# --- atualizar ---

def test_atualizar_modifica_nome_e_conteudo(conn_memoria):
    id = snippet_repo.salvar("nome original", "conteúdo original", conn=conn_memoria)
    snippet_repo.atualizar(id, "nome novo", "conteúdo novo", conn=conn_memoria)
    itens = snippet_repo.listar(conn=conn_memoria)
    assert itens[0]["name"] == "nome novo"
    assert itens[0]["content"] == "conteúdo novo"


def test_atualizar_nao_afeta_outros_snippets(conn_memoria):
    id1 = snippet_repo.salvar("primeiro", "a", conn=conn_memoria)
    id2 = snippet_repo.salvar("segundo", "b", conn=conn_memoria)
    snippet_repo.atualizar(id1, "primeiro atualizado", "a novo", conn=conn_memoria)
    por_id = {item["id"]: item for item in snippet_repo.listar(conn=conn_memoria)}
    assert por_id[id2]["name"] == "segundo"


def test_atualizar_id_inexistente_nao_levanta_excecao(conn_memoria):
    snippet_repo.atualizar(9999, "nome", "conteúdo", conn=conn_memoria)


# --- deletar ---

def test_deletar_remove_snippet(conn_memoria):
    id = snippet_repo.salvar("a deletar", "conteúdo", conn=conn_memoria)
    snippet_repo.deletar(id, conn=conn_memoria)
    itens = snippet_repo.listar(conn=conn_memoria)
    assert all(item["id"] != id for item in itens)


def test_deletar_id_inexistente_nao_levanta_excecao(conn_memoria):
    snippet_repo.deletar(9999, conn=conn_memoria)


def test_deletar_nao_afeta_outros_snippets(conn_memoria):
    id1 = snippet_repo.salvar("ficar", "conteúdo", conn=conn_memoria)
    id2 = snippet_repo.salvar("deletar", "conteúdo", conn=conn_memoria)
    snippet_repo.deletar(id2, conn=conn_memoria)
    itens = snippet_repo.listar(conn=conn_memoria)
    assert len(itens) == 1
    assert itens[0]["id"] == id1
