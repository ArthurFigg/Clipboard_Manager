# preview.py — DESCARTÁVEL. Não faz parte do app final.
# Uso: uv run python preview.py
# Semeia dados de exemplo no banco e abre a janela para visualização.

from db.connection import inicializar_banco
from db import history_repo, snippet_repo
from ui.app import App


def _semear_historico() -> None:
    if history_repo.listar(limite=1):
        return  # banco já tem dados, não sobrescreve

    amostras = [
        ("https://docs.python.org/3/library/sqlite3.html", "link"),
        ("https://github.com/TomSchimansky/CustomTkinter", "link"),
        ("arthur@exemplo.com.br", "email"),
        ("contato+suporte@empresa.com", "email"),
        (
            "def calcular_media(valores: list[float]) -> float:\n"
            "    return sum(valores) / len(valores)",
            "code",
        ),
        ("SELECT id, content, category\nFROM history\nORDER BY id DESC\nLIMIT 50;", "code"),
        ("import pandas as pd\ndf = pd.read_csv('dados.csv')", "code"),
        ("Reunião de alinhamento amanhã às 14h na sala 3", "text"),
        ("Lembrar de revisar o PR antes das 18h", "text"),
        ("1.234,56", "number"),
        ("(11) 98765-4321", "number"),
        ("[imagem 1920x1080]", "imagem"),
        ("C:\\Users\\Arthur\\Documents\\relatorio_mensal.pdf", "arquivo"),
        ("C:\\Users\\Arthur\\Downloads\\foto.jpg", "arquivo"),
        ("Texto simples copiado de um documento qualquer.", "text"),
    ]

    for conteudo, categoria in amostras:
        history_repo.salvar(conteudo, categoria)


def _semear_snippets() -> None:
    if snippet_repo.listar():
        return

    snippets = [
        (
            "Saudação formal",
            "Prezado(a),\n\nEspero que esta mensagem o encontre bem.\n\nAtenciosamente,",
        ),
        (
            "SQL — select paginado",
            "SELECT *\nFROM tabela\nWHERE ativo = 1\nORDER BY id DESC\nLIMIT 20 OFFSET 0;",
        ),
        (
            "Git — commit semântico",
            "git add -A && git commit -m 'feat: '",
        ),
        (
            "Python — list comprehension",
            "[item for item in lista if condicao(item)]",
        ),
    ]

    for nome, conteudo in snippets:
        snippet_repo.salvar(nome, conteudo)


if __name__ == "__main__":
    inicializar_banco()
    _semear_historico()
    _semear_snippets()

    app = App()
    app.deiconify()  # janela normalmente começa oculta — aqui exibimos direto
    app.mainloop()
