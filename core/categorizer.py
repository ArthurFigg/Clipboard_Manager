import re
from typing import Literal

Categoria = Literal["link", "email", "number", "code", "text"]

_LINK = re.compile(r"^https?://", re.IGNORECASE)
_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")
_NUMBER = re.compile(r"^[\d\s.,]+$")
_CODIGO = re.compile(r"def |class |import |\{|\}|=>|function |;")


def categorizar(conteudo: str) -> Categoria:
    texto = conteudo.strip()

    if _LINK.match(texto):
        return "link"

    if _EMAIL.match(texto):
        return "email"

    if _NUMBER.match(texto) and any(c.isdigit() for c in texto):
        return "number"

    if _CODIGO.search(conteudo):
        return "code"

    return "text"
