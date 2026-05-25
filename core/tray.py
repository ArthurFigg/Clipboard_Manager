import logging
import threading
from typing import Callable

import pystray
from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)


def _criar_icone() -> Image.Image:
    """Gera ícone de clipboard 64x64 para o system tray."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Corpo do clipboard
    draw.rounded_rectangle([10, 14, 54, 58], radius=5, fill=(59, 130, 246))
    # Clip no topo
    draw.rounded_rectangle([24, 8, 40, 20], radius=4, fill=(191, 219, 254))
    # Linhas de conteúdo
    for y in [28, 35, 42]:
        draw.rectangle([18, y, 46, y + 3], fill=(255, 255, 255, 200))
    return img


class GerenciadorTray:
    def __init__(
        self,
        callback_abrir: Callable,
        callback_alternar_autostart: Callable,
        callback_sair: Callable,
    ) -> None:
        self._callback_abrir = callback_abrir
        self._callback_alternar_autostart = callback_alternar_autostart
        self._callback_sair = callback_sair
        self._autostart_ativo = False
        self._icone: pystray.Icon | None = None

    def iniciar(self, autostart_ativo: bool = False) -> None:
        """Inicia o ícone de tray em thread daemon."""
        self._autostart_ativo = autostart_ativo

        menu = pystray.Menu(
            pystray.MenuItem(
                "Abrir",
                lambda icon, item: self._callback_abrir(),
                default=True,  # ação executada no duplo clique
            ),
            pystray.MenuItem(
                "Iniciar com Windows",
                lambda icon, item: self._alternar_autostart(),
                checked=lambda item: self._autostart_ativo,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Sair", lambda icon, item: self._parar_e_sair()),
        )

        self._icone = pystray.Icon(
            "clipboard_manager",
            _criar_icone(),
            "Clipboard Manager",
            menu,
        )

        thread = threading.Thread(target=self._icone.run, daemon=True)
        thread.start()
        logger.info("System tray iniciado")

    def atualizar_autostart(self, ativo: bool) -> None:
        """Atualiza o checkmark de autostart no menu sem recriar o ícone."""
        self._autostart_ativo = ativo
        if self._icone:
            self._icone.update_menu()

    def _alternar_autostart(self) -> None:
        self._callback_alternar_autostart()

    def _parar_e_sair(self) -> None:
        if self._icone:
            self._icone.stop()
        self._callback_sair()

    def parar(self) -> None:
        if self._icone:
            self._icone.stop()
            self._icone = None
