import queue
from unittest.mock import MagicMock, patch

from core.daemon import Daemon, _ler_clipboard


# ---------------------------------------------------------------------------
# _ler_clipboard
# ---------------------------------------------------------------------------

@patch("core.daemon.pyperclip.paste", return_value="texto simples")
@patch("PIL.ImageGrab.grabclipboard", return_value=None)
def test_ler_clipboard_retorna_texto(mock_grab, mock_paste):
    resultado = _ler_clipboard()
    assert resultado == ("texto simples", "text")


@patch("core.daemon.pyperclip.paste", return_value="https://exemplo.com")
@patch("PIL.ImageGrab.grabclipboard", return_value=None)
def test_ler_clipboard_categoriza_link(mock_grab, mock_paste):
    conteudo, categoria = _ler_clipboard()
    assert categoria == "link"


@patch("PIL.ImageGrab.grabclipboard", return_value=None)
@patch("core.daemon.pyperclip.paste", return_value="")
def test_ler_clipboard_retorna_none_para_texto_vazio(mock_paste, mock_grab):
    assert _ler_clipboard() is None


@patch("PIL.ImageGrab.grabclipboard", return_value=None)
@patch("core.daemon.pyperclip.paste", return_value="   ")
def test_ler_clipboard_retorna_none_para_apenas_espacos(mock_paste, mock_grab):
    assert _ler_clipboard() is None


def test_ler_clipboard_retorna_imagem():
    import base64, io
    from PIL import Image as PILImage

    # Usa imagem real para o save() funcionar corretamente
    imagem_real = PILImage.new("RGB", (1920, 1080), color=(255, 0, 0))

    with patch("PIL.ImageGrab.grabclipboard", return_value=imagem_real):
        resultado = _ler_clipboard()

    conteudo, categoria = resultado
    assert categoria == "imagem"
    dimensoes, b64 = conteudo.split(":", 1)
    assert dimensoes == "1920x1080"
    # Verifica roundtrip: base64 decodifica para PNG válido com tamanho correto
    recuperada = PILImage.open(io.BytesIO(base64.b64decode(b64)))
    assert recuperada.size == (1920, 1080)


def test_ler_clipboard_retorna_arquivo():
    caminhos = ["C:\\Users\\user\\doc.pdf", "C:\\Users\\user\\foto.jpg"]

    with patch("PIL.ImageGrab.grabclipboard", return_value=caminhos):
        resultado = _ler_clipboard()

    conteudo, categoria = resultado
    assert categoria == "arquivo"
    assert "C:\\Users\\user\\doc.pdf" in conteudo
    assert "C:\\Users\\user\\foto.jpg" in conteudo


@patch("core.daemon.pyperclip.paste", return_value="texto de fallback")
def test_ler_clipboard_usa_texto_quando_imagegrab_falha(mock_paste):
    with patch("PIL.ImageGrab.grabclipboard", side_effect=Exception("erro de formato")):
        resultado = _ler_clipboard()

    assert resultado == ("texto de fallback", "text")


@patch("PIL.ImageGrab.grabclipboard", side_effect=Exception("erro"))
@patch("core.daemon.pyperclip.paste", side_effect=Exception("erro de paste"))
def test_ler_clipboard_retorna_none_quando_tudo_falha(mock_paste, mock_grab):
    assert _ler_clipboard() is None


# ---------------------------------------------------------------------------
# Daemon._capturar
# ---------------------------------------------------------------------------

@patch("core.daemon.history_repo.salvar", return_value=1)
@patch("core.daemon._ler_clipboard", return_value=("texto novo", "text"))
def test_capturar_salva_conteudo_novo(mock_ler, mock_salvar):
    daemon = Daemon()
    daemon._capturar()
    mock_salvar.assert_called_once_with("texto novo", "text")


@patch("core.daemon.history_repo.salvar", return_value=1)
@patch("core.daemon._ler_clipboard", return_value=None)
def test_capturar_ignora_clipboard_vazio(mock_ler, mock_salvar):
    daemon = Daemon()
    daemon._capturar()
    mock_salvar.assert_not_called()


@patch("core.daemon.history_repo.salvar", return_value=1)
@patch("core.daemon._ler_clipboard", return_value=("mesmo conteúdo", "text"))
def test_capturar_ignora_duplicata_consecutiva(mock_ler, mock_salvar):
    daemon = Daemon()
    daemon._capturar()
    daemon._capturar()
    mock_salvar.assert_called_once()  # segunda chamada ignorada


@patch("core.daemon.history_repo.salvar", return_value=1)
@patch("core.daemon._ler_clipboard")
def test_capturar_salva_conteudo_alternado(mock_ler, mock_salvar):
    mock_ler.side_effect = [("texto A", "text"), ("texto B", "text"), ("texto A", "text")]
    daemon = Daemon()
    daemon._capturar()
    daemon._capturar()
    daemon._capturar()
    assert mock_salvar.call_count == 3


@patch("core.daemon.history_repo.salvar", return_value=1)
@patch("core.daemon._ler_clipboard", return_value=("conteúdo", "text"))
def test_capturar_atualiza_ultimo_conteudo(mock_ler, mock_salvar):
    daemon = Daemon()
    daemon._capturar()
    assert daemon._ultimo_conteudo == "conteúdo"


@patch("core.daemon.history_repo.salvar", return_value=42)
@patch("core.daemon._ler_clipboard", return_value=("conteúdo", "text"))
def test_capturar_envia_evento_para_fila(mock_ler, mock_salvar):
    fila = queue.Queue()
    daemon = Daemon(fila=fila)
    daemon._capturar()

    evento = fila.get_nowait()
    assert evento["id"] == 42
    assert evento["content"] == "conteúdo"
    assert evento["category"] == "text"


@patch("core.daemon.history_repo.salvar", return_value=1)
@patch("core.daemon._ler_clipboard", return_value=("conteúdo", "text"))
def test_capturar_sem_fila_nao_levanta_excecao(mock_ler, mock_salvar):
    daemon = Daemon(fila=None)
    daemon._capturar()  # não deve lançar


@patch("core.daemon.history_repo.salvar", return_value=1)
@patch("core.daemon._ler_clipboard", return_value=("conteúdo", "text"))
def test_capturar_fila_permanece_vazia_em_duplicata(mock_ler, mock_salvar):
    fila = queue.Queue()
    daemon = Daemon(fila=fila)
    daemon._capturar()
    daemon._capturar()  # duplicata — não envia para fila
    assert fila.qsize() == 1


# ---------------------------------------------------------------------------
# Daemon — ciclo de vida
# ---------------------------------------------------------------------------

def test_iniciar_define_flag_ativo():
    daemon = Daemon()
    with patch("core.daemon._ler_clipboard", return_value=None):
        daemon.iniciar()
        assert daemon._ativo is True
        daemon.parar()


def test_iniciar_idempotente():
    daemon = Daemon()
    with patch("core.daemon._ler_clipboard", return_value=None):
        daemon.iniciar()
        thread_original = daemon._thread
        daemon.iniciar()  # segunda chamada não cria nova thread
        assert daemon._thread is thread_original
        daemon.parar()


def test_parar_desativa_flag():
    daemon = Daemon()
    with patch("core.daemon._ler_clipboard", return_value=None):
        daemon.iniciar()
        daemon.parar()
        assert daemon._ativo is False


def test_thread_e_daemon():
    """Thread criada deve ser daemon para não bloquear o shutdown do processo."""
    daemon = Daemon()
    with patch("core.daemon._ler_clipboard", return_value=None):
        daemon.iniciar()
        assert daemon._thread.daemon is True
        daemon.parar()
