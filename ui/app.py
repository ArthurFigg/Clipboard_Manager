import queue

import customtkinter as ctk

from ui.history_tab import HistoricoTab
from ui.snippets_tab import SnippetsTab

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

_INTERVALO_POLLING_MS = 500


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Clipboard Manager")
        self.geometry("640x520")
        self.minsize(480, 400)
        self.withdraw()  # começa oculta — hotkey ou tray a exibe

        abas = ctk.CTkTabview(self)
        abas.pack(fill="both", expand=True, padx=10, pady=10)

        abas.add("Histórico")
        abas.add("Snippets")

        self._aba_historico = HistoricoTab(abas.tab("Histórico"))
        self._aba_historico.pack(fill="both", expand=True)

        self._aba_snippets = SnippetsTab(abas.tab("Snippets"))
        self._aba_snippets.pack(fill="both", expand=True)

        self._fila: queue.Queue | None = None

        # X fecha para o tray em vez de encerrar o processo
        self.protocol("WM_DELETE_WINDOW", self.withdraw)

    def iniciar_polling_fila(self, fila: queue.Queue) -> None:
        """Conecta a fila do daemon e inicia o polling na thread da UI."""
        self._fila = fila
        self._processar_fila()

    def _processar_fila(self) -> None:
        while self._fila and not self._fila.empty():
            try:
                evento = self._fila.get_nowait()
                self._aba_historico.adicionar_item(evento)
            except Exception:
                pass
        self.after(_INTERVALO_POLLING_MS, self._processar_fila)

    def alternar_visibilidade(self) -> None:
        """Mostra ou oculta a janela. Chamado pela hotkey e pelo tray."""
        if self.winfo_viewable():
            self.withdraw()
        else:
            self.deiconify()
            self.lift()
            self.focus_force()
