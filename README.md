# Clipboard Manager

Utilitário desktop para Windows que monitora o clipboard em segundo plano, categoriza automaticamente tudo que você copia e mantém um histórico pesquisável com suporte a texto, imagens e arquivos.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Funcionalidades

- **Captura automática** — monitora o clipboard a cada 0,5 s sem interferir no fluxo de trabalho
- **Categorização inteligente** — classifica cada item em: `link`, `email`, `number`, `code`, `text`, `imagem` ou `arquivo`
- **Histórico pesquisável** — busca por texto e filtro por categoria; até 500 itens persistidos em SQLite
- **Re-cópia real de imagens** — imagens são armazenadas em base64 e restauradas para o clipboard via API nativa do Windows (CF_DIB)
- **Snippets fixos** — crie, edite e delete trechos de texto reutilizáveis que não somem do histórico
- **Exportação** — exporte o histórico ou snippets em `.txt`, `.json` ou `.md`
- **Hotkey global** — `Ctrl+Shift+V` abre/fecha a janela de qualquer lugar (configurável)
- **System tray** — ícone na bandeja; fechar a janela não encerra o app
- **Autostart** — opção de iniciar com o Windows via registro `HKCU\...\Run`

---

## Pré-requisitos

- Windows 10/11
- Python 3.11+
- [`uv`](https://github.com/astral-sh/uv) (gerenciador de dependências)

---

## Instalação

```bash
# Clone o repositório
git clone https://github.com/ArthurFigg/Clipboard_Manager.git
cd Clipboard_Manager

# Instale as dependências
uv sync
```

---

## Uso

```bash
uv run main.py
```

O app inicia **oculto**. Para abrir a janela use a hotkey `Ctrl+Shift+V` ou clique no ícone da bandeja do sistema.

### Primeira execução

Na primeira execução são criados automaticamente:

| Caminho | Conteúdo |
|---|---|
| `%LOCALAPPDATA%\ClipboardManager\data.db` | Banco SQLite com histórico e snippets |
| `%LOCALAPPDATA%\ClipboardManager\config.json` | Configurações do usuário |

---

## Interface

### Aba Histórico

| Elemento | Ação |
|---|---|
| Clique em um item | Re-copia para o clipboard |
| Campo de busca | Filtra por conteúdo em tempo real |
| Dropdown de categoria | Filtra por tipo |
| `✕` no item | Remove do histórico |
| Botão "Limpar histórico" | Remove todos os itens |

### Aba Snippets

| Elemento | Ação |
|---|---|
| Clique em um item | Re-copia para o clipboard |
| `+ Novo snippet` | Abre formulário para criar snippet |
| `✎` no item | Edita nome e conteúdo |
| `✕` no item | Deleta o snippet |

---

## Configuração

O arquivo `%LOCALAPPDATA%\ClipboardManager\config.json` é criado automaticamente com os valores padrão:

```json
{
  "hotkey": "<ctrl>+<shift>+v",
  "limite_historico": 500,
  "autostart": false
}
```

| Chave | Tipo | Descrição |
|---|---|---|
| `hotkey` | string | Combinação de teclas para abrir/fechar a janela |
| `limite_historico` | int | Máximo de itens mantidos no histórico |
| `autostart` | bool | Iniciar automaticamente com o Windows |

O autostart também pode ser ativado/desativado pelo menu do tray.

---

## Estrutura do projeto

```
clipboard_manager/
├── main.py              # Ponto de entrada — conecta todos os módulos
├── config.py            # Leitura e escrita de config.json
├── pyproject.toml
│
├── core/
│   ├── daemon.py        # Thread de monitoramento do clipboard
│   ├── categorizer.py   # Categorização por regex (função pura)
│   ├── hotkey.py        # Hotkey global via pynput
│   ├── tray.py          # System tray via pystray
│   └── autostart.py     # Registro de autostart via winreg
│
├── db/
│   ├── connection.py    # Criação do banco e tabelas
│   ├── history_repo.py  # CRUD do histórico
│   └── snippet_repo.py  # CRUD dos snippets
│
├── ui/
│   ├── app.py           # Janela principal (CustomTkinter)
│   ├── history_tab.py   # Aba de histórico
│   └── snippets_tab.py  # Aba de snippets
│
├── export/
│   └── exporter.py      # Exportação para txt / json / md
│
└── tests/               # 135 testes com pytest
```

---

## Testes

```bash
uv run pytest -v
```

135 testes cobrindo categorizer, repositórios, daemon, exporter, hotkey, autostart e config.

---

## Dependências

| Pacote | Uso |
|---|---|
| `customtkinter` | Interface gráfica moderna sobre Tkinter |
| `pillow` | Leitura de imagens do clipboard (`ImageGrab`) |
| `pynput` | Hotkey global |
| `pyperclip` | Leitura e escrita de texto no clipboard |
| `pystray` | Ícone na bandeja do sistema |

---

## Licença

MIT