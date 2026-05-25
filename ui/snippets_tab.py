import pyperclip
import customtkinter as ctk

from db import snippet_repo


class SnippetsTab(ctk.CTkFrame):
    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._construir_layout()
        self.atualizar()

    def _construir_layout(self) -> None:
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", padx=10, pady=(10, 6))

        ctk.CTkButton(
            barra,
            text="+ Novo snippet",
            command=lambda: self._abrir_formulario(None),
        ).pack(side="left")

        self._status = ctk.CTkLabel(self, text="", text_color=("gray50", "gray60"),
                                    font=ctk.CTkFont(size=11))
        self._status.pack(anchor="w", padx=12)

        self._lista = ctk.CTkScrollableFrame(self)
        self._lista.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def atualizar(self) -> None:
        itens = snippet_repo.listar()
        self._renderizar(itens)

    def _renderizar(self, itens) -> None:
        for w in self._lista.winfo_children():
            w.destroy()

        for item in itens:
            self._criar_card(dict(item))

    def _criar_card(self, item: dict) -> None:
        card = ctk.CTkFrame(self._lista, fg_color=("gray92", "gray18"), corner_radius=8)
        card.pack(fill="x", pady=4, padx=2)
        card.configure(cursor="hand2")

        # Linha do título com botões
        titulo_frame = ctk.CTkFrame(card, fg_color="transparent")
        titulo_frame.pack(fill="x", padx=8, pady=(8, 2))

        # Botões empacotados ANTES do nome — regra do tkinter: side="right" primeiro,
        # depois o widget que preenche o espaço restante à esquerda
        btn_del = ctk.CTkButton(
            titulo_frame, text="✕", width=26, height=22,
            fg_color="transparent", hover_color=("gray80", "gray30"),
            command=lambda id=item["id"]: self._deletar(id),
        )
        btn_del.pack(side="right", padx=(2, 0))

        btn_edit = ctk.CTkButton(
            titulo_frame, text="✎", width=26, height=22,
            fg_color="transparent", hover_color=("gray80", "gray30"),
            command=lambda i=item: self._abrir_formulario(i),
        )
        btn_edit.pack(side="right", padx=(0, 2))

        nome = ctk.CTkLabel(
            titulo_frame, text=item["name"], anchor="w",
            font=ctk.CTkFont(weight="bold"),
        )
        nome.pack(side="left", fill="x", expand=True)

        # Preview do conteúdo
        preview = item["content"][:100].replace("\n", " ")
        ctk.CTkLabel(
            card, text=preview, anchor="w", justify="left",
            text_color=("gray45", "gray65"), font=ctk.CTkFont(size=11),
        ).pack(fill="x", padx=8, pady=(0, 8))

        # Clique no card re-copia
        conteudo = item["content"]
        for widget in (card, nome):
            widget.bind("<Button-1>", lambda _e, c=conteudo: self._recopiar(c))

    def _recopiar(self, conteudo: str) -> None:
        pyperclip.copy(conteudo)
        self._mostrar_status(f"Copiado: {conteudo[:40].replace(chr(10), ' ')}")

    def _mostrar_status(self, mensagem: str) -> None:
        self._status.configure(text=mensagem)
        self.after(2000, lambda: self._status.configure(text=""))

    def _deletar(self, id: int) -> None:
        snippet_repo.deletar(id)
        self.atualizar()

    def _abrir_formulario(self, item: dict | None) -> None:
        FormularioSnippet(self, item=item, callback=self.atualizar)


class FormularioSnippet(ctk.CTkToplevel):
    def __init__(self, parent, item: dict | None = None, callback=None) -> None:
        super().__init__(parent)
        self._item = item
        self._callback = callback
        self._construir()

    def _construir(self) -> None:
        titulo = "Editar snippet" if self._item else "Novo snippet"
        self.title(titulo)
        self.geometry("420x320")
        self.resizable(False, False)
        # grab_set após renderização para evitar problema de timing no Windows
        self.after(100, self.grab_set)

        ctk.CTkLabel(self, text="Nome").pack(anchor="w", padx=16, pady=(16, 4))
        self._campo_nome = ctk.CTkEntry(self, placeholder_text="Nome do snippet")
        self._campo_nome.pack(fill="x", padx=16)

        ctk.CTkLabel(self, text="Conteúdo").pack(anchor="w", padx=16, pady=(12, 4))
        self._campo_conteudo = ctk.CTkTextbox(self, height=130)
        self._campo_conteudo.pack(fill="x", padx=16)

        if self._item:
            self._campo_nome.insert(0, self._item["name"])
            self._campo_conteudo.insert("1.0", self._item["content"])

        rodape = ctk.CTkFrame(self, fg_color="transparent")
        rodape.pack(fill="x", padx=16, pady=12)

        ctk.CTkButton(rodape, text="Cancelar", width=90,
                      fg_color=("gray75", "gray30"),
                      hover_color=("gray65", "gray25"),
                      text_color=("gray10", "gray90"),
                      command=self.destroy).pack(side="right", padx=(6, 0))
        ctk.CTkButton(rodape, text="Salvar", width=90,
                      command=self._salvar).pack(side="right")

    def _salvar(self) -> None:
        nome = self._campo_nome.get().strip()
        conteudo = self._campo_conteudo.get("1.0", "end-1c").strip()

        if not nome or not conteudo:
            return

        if self._item:
            snippet_repo.atualizar(self._item["id"], nome, conteudo)
        else:
            snippet_repo.salvar(nome, conteudo)

        if self._callback:
            self._callback()
        self.destroy()
