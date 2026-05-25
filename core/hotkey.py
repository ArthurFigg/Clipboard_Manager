import logging
from typing import Callable

from pynput.keyboard import GlobalHotKeys

logger = logging.getLogger(__name__)

COMBINACAO_PADRAO = "<ctrl>+<shift>+v"


class GerenciadorHotkey:
    def __init__(
        self,
        callback: Callable,
        combinacao: str = COMBINACAO_PADRAO,
    ) -> None:
        self._callback = callback
        self._combinacao = combinacao
        self._listener: GlobalHotKeys | None = None

    def iniciar(self) -> None:
        """Inicia a escuta da hotkey em thread daemon. Idempotente."""
        if self._listener:
            return
        self._listener = GlobalHotKeys({self._combinacao: self._callback})
        self._listener.start()
        logger.info("Hotkey registrada: %s", self._combinacao)

    def parar(self) -> None:
        """Para a escuta da hotkey."""
        if self._listener:
            self._listener.stop()
            self._listener = None
            logger.info("Hotkey removida: %s", self._combinacao)

    def trocar_combinacao(self, nova: str) -> None:
        """Troca a hotkey sem reiniciar o app."""
        self.parar()
        self._combinacao = nova
        self.iniciar()

    @property
    def combinacao(self) -> str:
        return self._combinacao
