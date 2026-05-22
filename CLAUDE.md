# Clipboard Manager

## Objetivo
Utilitário desktop que roda em segundo plano e captura tudo que o usuário copia. Categoriza automaticamente por tipo, mantém histórico pesquisável e persistente, oferece uma aba de snippets fixos gerenciáveis pelo usuário e permite exportar os dados em múltiplos formatos.

---

## Stack
- **Python 3.11+**
- **CustomTkinter** — interface gráfica
- **pynput** — hotkey global para abrir/fechar a janela
- **pyperclip** — leitura e escrita no clipboard
- **SQLite (sqlite3)** — persistência do histórico e snippets
- **threading** — daemon de monitoramento em background
- **re** — detecção de categoria por regex
- **json / pathlib** — exportação de dados
- **pytest** — testes unitários
- **uv** — gerenciamento de dependências

---

## Estrutura de pastas sugerida

```
clipboard_manager/
├── main.py                  # Ponto de entrada: inicializa daemon e UI
├── pyproject.toml
│
├── core/
│   ├── __init__.py
│   ├── daemon.py            # Thread de monitoramento do clipboard
│   ├── categorizer.py       # Lógica de categorização por regex
│   └── hotkey.py            # Registro e escuta da hotkey global
│
├── db/
│   ├── __init__.py
│   ├── connection.py        # Conexão e criação das tabelas
│   ├── history_repo.py      # CRUD do histórico
│   └── snippet_repo.py      # CRUD dos snippets
│
├── ui/
│   ├── __init__.py
│   ├── app.py               # Janela principal (CTk), controla abas
│   ├── history_tab.py       # Aba de histórico: lista, busca, filtro por categoria
│   └── snippets_tab.py      # Aba de snippets: criar, editar, deletar, re-copiar
│
├── export/
│   ├── __init__.py
│   └── exporter.py          # Exportação para .txt, .json, .md
│
└── tests/
    ├── test_categorizer.py
    ├── test_history_repo.py
    ├── test_snippet_repo.py
    └── test_exporter.py
```

---

## Banco de dados

### Tabela `history`
| Campo       | Tipo    | Descrição                                      |
|-------------|---------|------------------------------------------------|
| id          | INTEGER | PK autoincrement                               |
| content     | TEXT    | Conteúdo copiado                               |
| category    | TEXT    | link / code / email / number / text / imagem / arquivo |
| copied_at   | TEXT    | Timestamp ISO 8601                             |

### Tabela `snippets`
| Campo       | Tipo    | Descrição                                      |
|-------------|---------|------------------------------------------------|
| id          | INTEGER | PK autoincrement                               |
| name        | TEXT    | Nome dado pelo usuário                         |
| content     | TEXT    | Conteúdo do snippet                            |
| created_at  | TEXT    | Timestamp ISO 8601                             |

---

## Categorização automática

Conteúdo não-texto é categorizado antes da detecção por regex:

0. **imagem** — clipboard contém bitmap/imagem
1. **arquivo** — clipboard contém um ou mais caminhos de arquivo

Para conteúdo textual, detectar por regex na seguinte ordem de prioridade:

2. **link** — começa com `http://` ou `https://`
3. **email** — padrão `usuario@dominio.ext`
4. **number** — apenas dígitos, pontos, vírgulas e espaços (ex: CPF, telefone, valores)
5. **code** — contém pelo menos um dos: `def `, `class `, `import `, `{`, `}`, `=>`, `function`, `;`
6. **text** — qualquer coisa que não se encaixe nas anteriores

---

## Funcionalidades por módulo

### `core/daemon.py`
- Loop em thread daemon
- Lê clipboard a cada 0.5s com `pyperclip.paste()`
- Compara com o último item capturado para evitar duplicatas consecutivas
- Chama `categorizer` e salva no banco via `history_repo`
- Respeita um limite de 500 itens no histórico (remove os mais antigos)

### `core/hotkey.py`
- Registra atalho global (sugestão: `Ctrl+Shift+V`) com `pynput`
- Ao acionar: mostra ou esconde a janela principal

### `ui/history_tab.py`
- Lista rolável com os itens do histórico (mais recente no topo)
- Campo de busca por texto (filtra em tempo real)
- Filtro por categoria (dropdown ou botões de toggle)
- Clique em item: re-copia para o clipboard
- Botão de deletar item individual
- Botão "Limpar histórico"

### `ui/snippets_tab.py`
- Lista de snippets com nome e preview do conteúdo
- Botão "Novo snippet": abre formulário com campo nome + campo conteúdo
- Botão editar e deletar por item
- Clique em item: re-copia para o clipboard

### `export/exporter.py`
- Recebe lista de itens (histórico ou snippets) e formato desejado
- `.txt` — um item por linha
- `.json` — array de objetos com todos os campos
- `.md` — tabela markdown com categoria, conteúdo e data

---

## Status de implementação

### Concluído

- **Etapa 1 — Setup**: `pyproject.toml` + estrutura de pastas + venv via `uv`. Dependências: `customtkinter 5.2.2`, `pynput 1.8.2`, `pyperclip 1.11.0`, `pytest 9.0.3`.
- **Etapa 2 — Banco**: `db/connection.py` — cria `%LOCALAPPDATA%\ClipboardManager\data.db` e tabelas `history` e `snippets` na primeira execução. Conexão por operação (`obter_conexao()`) para segurança com threads.
- **Etapa 3 — Categorizer**: `core/categorizer.py` — função pura `categorizar(conteudo) -> Categoria`. 28 testes passando em `tests/test_categorizer.py`. Nota: qualquer `;` isolado dispara `code` — heurística aceita pelo spec, pode ser refinada no futuro.

### Próximas etapas

- **Etapa 4 — Repositórios**: `db/history_repo.py` + `db/snippet_repo.py` + testes dos dois. Mesma etapa por dependência idêntica (`connection.py`) e estrutura similar.
- **Etapa 5 — Daemon**: `core/daemon.py` — thread de captura com `pyperclip`, detecção de imagem/arquivo antes do categorizer, salva via `history_repo`. Comunicação com UI via `queue.Queue`.
- **Etapa 6 — Exporter**: `export/exporter.py` + testes. Função pura, sem dependências externas.
- **Etapa 7 — UI**: `ui/app.py` + `ui/history_tab.py` + `ui/snippets_tab.py`. Oferecer `preview.py` descartável antes da integração final.
- **Etapa 8 — Hotkey, tray e autostart**: `core/hotkey.py` + system tray + registro no Windows. Integração ao `main.py`.
- **Etapa 9 — Integração final**: `main.py` completo, `config.json`, testes de integração, ajustes de UI.

---

## Configurações e persistência

- **Banco de dados**: `%LOCALAPPDATA%\ClipboardManager\data.db` — criado automaticamente na primeira execução
- **Arquivo de configuração**: `%LOCALAPPDATA%\ClipboardManager\config.json` — salva preferências do usuário
- Configurações persistidas: hotkey, limite do histórico, autostart ativo/inativo

---

## Comportamento com clipboard não-texto

- Quando o clipboard contém imagem: categoria `imagem`, content salva dimensões ou descrição genérica (`[imagem]`)
- Quando o clipboard contém arquivo(s): categoria `arquivo`, content salva o(s) caminho(s) completo(s) separados por newline
- Erros de leitura do clipboard (ex: formato não suportado) são logados e ignorados silenciosamente — daemon não para

---

## Startup e tray

- O app registra autostart no Windows via `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- Ícone no system tray sempre visível enquanto o app roda
- Menu do tray: Abrir, Ativar/Desativar autostart, Sair
- Toggle de autostart disponível no tray e na UI — deve refletir o estado real do registro do Windows
- Janela começa oculta — só aparece ao acionar a hotkey ou clicar no tray

---

## Hotkey

- Padrão: `Ctrl+Shift+V` — configurável pelo usuário via UI
- Hotkey é salva em `config.json` e recarregada sem reiniciar o app
- Se a hotkey colidir com outro app, o usuário vê aviso e pode trocar na hora

---

## Regras de desenvolvimento

- Cada módulo tem responsabilidade única — UI não acessa banco diretamente, sempre via repositório
- O daemon nunca toca na UI diretamente — comunicação via fila thread-safe (`queue.Queue`) se necessário
- Categorização é stateless — função pura que recebe string e retorna categoria
- Exportação é stateless — função pura que recebe lista e retorna string formatada
- Não salvar itens em branco ou com apenas espaços no histórico
- Manter cobertura de testes nos módulos de lógica (categorizer, repos, exporter)
