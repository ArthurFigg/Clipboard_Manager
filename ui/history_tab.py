import base64
import ctypes
import io
import logging

import pyperclip
import customtkinter as ctk
from PIL import Image

from db import history_repo

logger = logging.getLogger(__name__)

CATEGORIAS = ["todas", "link", "email", "number", "code", "text", "imagem", "arquivo"]

_COR_TAG = {
    "link":    ("#1d6fa4", "#4db8ff"),
    "email":   ("#6a1d9a", "#c77dff"),
    "number":  ("#1a6b35", "#52c788"),
    "code":    ("#7a4000", "#ffb347"),
    "text":    ("#444444", "#aaaaaa"),
    "imagem":  ("#7a1f3c", "#ff6b9d"),
    "arquivo": ("#2d4a7a", "#7eb8f7"),
}

_CF_DIB = 8
_GMEM_MOVEABLE = 0x0002


def _colocar_imagem_no_clipboard(conteudo_imagem: str) -> None:
    """Decodifica base64 PNG e coloca a imagem no clipboard do Windows via ctypes."""
    b64 = conteudo_imagem.split(":", 1)[1]
    dados_png = base64.b64decode(b64)
    imagem = Image.open(io.BytesIO(dados_png)).convert("RGB")

    # CF_DIB espera BITMAPINFOHEADER + pixels — BMP tem 14 bytes de cabeçalho de arquivo a mais
    buf = io.BytesIO()
    imagem.save(buf, "BMP")
    dados_dib = buf.getvalue()[14:]

    ctypes.windll.user32.OpenClipboard(None)
    try:
        ctypes.windll.user32.EmptyClipboard()
        h_mem = ctypes.windll.kernel32.GlobalAlloc(_GMEM_MOVEABLE, len(dados_dib))
        ptr = ctypes.windll.kernel32.GlobalLock(h_mem)
        ctypes.memmove(ptr, dados_dib, len(dados_dib))
        ctypes.windll.kernel32.GlobalUnlock(h_mem)
        ctypes.windll.user32.SetClipboardData(_CF_DIB, h_mem)
    finally:
        ctypes.windll.user32.CloseClipboard()


class HistoricoTab(ctk.CTkFrame):
    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._construir_layout()
        self.atualizar()

    def _construir_layout(self) -> None:
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", padx=10, pady=(10, 6))

        self._campo_busca = ctk.CTkEntry(barra, placeholder_text="Buscar...", width=200)
        self._campo_busca.pack(side="left", padx=(0, 8))
        self._campo_busca.bind("<KeyRelease>", lambda _e: self.atualizar())

        self._filtro_categoria = ctk.CTkOptionMenu(
            barra,
            values=CATEGORIAS,
            command=lambda _: self.atualizar(),
            width=110,
        )
        self._filtro_categoria.pack(side="left")

        ctk.CTkButton(
            barra,
            text="Limpar histórico",
            width=130,
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray25"),
            text_color=("gray10", "gray90"),
            command=self._limpar,
        ).pack(side="right")

        self._status = ctk.CTkLabel(self, text="", text_color=("gray50", "gray60"),
                                    font=ctk.CTkFont(size=11))
        self._status.pack(anchor="w", padx=12)

        self._lista = ctk.CTkScrollableFrame(self)
        self._lista.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def atualizar(self) -> None:
        busca = self._campo_busca.get().strip() or None
        selecionada = self._filtro_categoria.get()
        categoria = None if selecionada == "todas" else selecionada

        itens = history_repo.listar(limite=200, categoria=categoria, busca=busca)
        self._renderizar(itens)

    def _renderizar(self, itens) -> None:
        for w in self._lista.winfo_children():
            w.destroy()

        for item in itens:
            self._criar_linha(dict(item))

    def _criar_linha(self, item: dict) -> None:
        linha = ctk.CTkFrame(self._lista, fg_color=("gray92", "gray18"), corner_radius=6)
        linha.pack(fill="x", pady=2, padx=2)
        linha.configure(cursor="hand2")

        cat = item["category"]
        cor = _COR_TAG.get(cat, ("#444444", "#aaaaaa"))
        tag = ctk.CTkLabel(
            linha, text=cat, width=62, anchor="center",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=cor, fg_color="transparent",
        )
        tag.pack(side="left", padx=(8, 6), pady=6)

        # Imagens armazenam "WxH:<base64>" — exibe só as dimensões
        if cat == "imagem":
            dimensoes = item["content"].split(":", 1)[0]
            preview = f"[imagem {dimensoes}]"
        else:
            preview = item["content"][:90].replace("\n", " ")

        label = ctk.CTkLabel(linha, text=preview, anchor="w", justify="left")
        label.pack(side="left", fill="x", expand=True, pady=6)

        btn_del = ctk.CTkButton(
            linha, text="✕", width=26, height=22,
            fg_color="transparent", hover_color=("gray80", "gray30"),
            command=lambda id=item["id"]: self._deletar(id),
        )
        btn_del.pack(side="right", padx=6)

        conteudo = item["content"]
        categoria = item["category"]
        for widget in (linha, tag, label):
            widget.bind(
                "<Button-1>",
                lambda _e, c=conteudo, cat=categoria: self._recopiar(c, cat),
            )

    def _recopiar(self, conteudo: str, categoria: str) -> None:
        try:
            if categoria == "imagem":
                _colocar_imagem_no_clipboard(conteudo)
                dimensoes = conteudo.split(":", 1)[0]
                self._mostrar_status(f"Copiado: [imagem {dimensoes}]")
            else:
                pyperclip.copy(conteudo)
                self._mostrar_status(f"Copiado: {conteudo[:40].replace(chr(10), ' ')}")
        except Exception as e:
            logger.error("Erro ao re-copiar: %s", e)
            self._mostrar_status("Erro ao copiar item")

    def _mostrar_status(self, mensagem: str) -> None:
        self._status.configure(text=mensagem)
        self.after(2000, lambda: self._status.configure(text=""))

    def _deletar(self, id: int) -> None:
        history_repo.deletar(id)
        self.atualizar()

    def _limpar(self) -> None:
        history_repo.limpar()
        self.atualizar()

    def adicionar_item(self, _evento: dict) -> None:
        """Chamado pela App quando o daemon emite novo item via fila."""
        self.atualizar()
