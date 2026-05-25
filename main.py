import logging
import queue

import config as cfg
from core.autostart import ativar as autostart_ativar
from core.autostart import desativar as autostart_desativar
from core.autostart import esta_ativo as autostart_ativo
from core.daemon import Daemon
from core.hotkey import GerenciadorHotkey
from core.tray import GerenciadorTray
from db.connection import inicializar_banco
from ui.app import App

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-24s  %(levelname)s  %(message)s",
)
logger = logging.getLogger(__name__)


def iniciar() -> None:
    # --- infraestrutura ---
    inicializar_banco()
    config = cfg.carregar()
    logger.info("Config carregado: %s", config)

    fila: queue.Queue = queue.Queue()

    # --- UI (começa oculta) ---
    app = App()
    app.iniciar_polling_fila(fila)

    # --- daemon de captura ---
    daemon = Daemon(fila=fila)
    daemon.iniciar()

    # --- hotkey ---
    # Callback é chamado na thread do pynput; after(0) garante execução na UI
    def _alternar_visibilidade() -> None:
        app.after(0, app.alternar_visibilidade)

    hotkey = GerenciadorHotkey(_alternar_visibilidade, config["hotkey"])
    hotkey.iniciar()

    # --- tray ---
    # A variável tray é usada dentro de _sair, declarada antes para evitar
    # referência antes da atribuição (Python fecha sobre a variável, não o valor)
    tray_ref: list[GerenciadorTray] = []

    def _abrir() -> None:
        app.after(0, app.deiconify)
        app.after(0, app.lift)
        app.after(0, app.focus_force)

    def _alternar_autostart() -> None:
        if autostart_ativo():
            autostart_desativar()
        else:
            autostart_ativar()
        ativo = autostart_ativo()
        tray_ref[0].atualizar_autostart(ativo)
        config["autostart"] = ativo
        cfg.salvar(config)
        logger.info("Autostart %s", "ativado" if ativo else "desativado")

    def _sair() -> None:
        logger.info("Encerrando...")
        daemon.parar()
        hotkey.parar()
        # destroy precisa rodar na thread da UI
        app.after(0, _encerrar_app)

    def _encerrar_app() -> None:
        if tray_ref:
            tray_ref[0].parar()
        app.destroy()

    tray = GerenciadorTray(
        callback_abrir=_abrir,
        callback_alternar_autostart=_alternar_autostart,
        callback_sair=_sair,
    )
    tray_ref.append(tray)
    tray.iniciar(autostart_ativo=autostart_ativo())

    logger.info("Clipboard Manager iniciado. Hotkey: %s", config["hotkey"])

    # --- mainloop (bloqueia até app.destroy()) ---
    app.mainloop()

    logger.info("Clipboard Manager encerrado.")


if __name__ == "__main__":
    iniciar()
