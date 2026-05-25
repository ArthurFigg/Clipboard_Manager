import base64
import io
import logging
import queue
import threading
import time

import pyperclip
from PIL import ImageGrab

from core.categorizer import categorizar
from db import history_repo

logger = logging.getLogger(__name__)

INTERVALO_CAPTURA = 0.5  # segundos


def _ler_clipboard() -> tuple[str, str] | None:
    """
    Lê o conteúdo atual do clipboard.
    Retorna (conteudo, categoria) ou None se vazio ou ilegível.
    Prioridade: imagem → arquivo → texto.
    """
    try:
        # ImageGrab.grabclipboard() retorna Image, list[str] ou None
        captura = ImageGrab.grabclipboard()

        if isinstance(captura, list):
            conteudo = "\n".join(captura)
            return conteudo, "arquivo"

        if captura is not None:
            # Salva PNG em base64 — formato "WxH:<base64>" permite re-cópia real
            buf = io.BytesIO()
            captura.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode()
            return f"{captura.width}x{captura.height}:{b64}", "imagem"

    except Exception as e:
        # Formato não suportado pelo ImageGrab — segue para leitura de texto
        logger.debug("Erro ao ler clipboard não-texto: %s", e)

    try:
        texto = pyperclip.paste()
        if not texto or not texto.strip():
            return None
        return texto, categorizar(texto)
    except Exception as e:
        logger.debug("Erro ao ler clipboard texto: %s", e)
        return None


class Daemon:
    def __init__(self, fila: queue.Queue | None = None) -> None:
        self._fila = fila
        self._ultimo_conteudo: str | None = None
        self._ativo = False
        self._thread: threading.Thread | None = None

    def iniciar(self) -> None:
        """Inicia a thread daemon de captura. Idempotente."""
        if self._ativo:
            return
        self._ativo = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        logger.info("Daemon de clipboard iniciado")

    def parar(self) -> None:
        """Sinaliza a thread para encerrar no próximo ciclo."""
        self._ativo = False
        logger.info("Daemon de clipboard parado")

    def _loop(self) -> None:
        while self._ativo:
            try:
                self._capturar()
            except Exception as e:
                # Erro isolado não derruba o daemon
                logger.error("Erro no loop do daemon: %s", e)
            time.sleep(INTERVALO_CAPTURA)

    def _capturar(self) -> None:
        """Lê o clipboard e persiste se for conteúdo novo."""
        resultado = _ler_clipboard()
        if resultado is None:
            return

        conteudo, categoria = resultado

        if conteudo == self._ultimo_conteudo:
            return

        self._ultimo_conteudo = conteudo
        id_item = history_repo.salvar(conteudo, categoria)

        if self._fila is not None:
            self._fila.put({"id": id_item, "content": conteudo, "category": categoria})

        logger.debug("Capturado: [%s] %s...", categoria, conteudo[:50])
