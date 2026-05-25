from unittest.mock import MagicMock, patch

from core.hotkey import GerenciadorHotkey, COMBINACAO_PADRAO


# --- iniciar ---

@patch("core.hotkey.GlobalHotKeys")
def test_iniciar_cria_listener_com_combinacao_padrao(mock_hotkeys_class):
    callback = MagicMock()
    gerenciador = GerenciadorHotkey(callback)
    gerenciador.iniciar()
    mock_hotkeys_class.assert_called_once_with({COMBINACAO_PADRAO: callback})


@patch("core.hotkey.GlobalHotKeys")
def test_iniciar_chama_start_no_listener(mock_hotkeys_class):
    mock_listener = MagicMock()
    mock_hotkeys_class.return_value = mock_listener
    GerenciadorHotkey(MagicMock()).iniciar()
    mock_listener.start.assert_called_once()


@patch("core.hotkey.GlobalHotKeys")
def test_iniciar_com_combinacao_customizada(mock_hotkeys_class):
    callback = MagicMock()
    gerenciador = GerenciadorHotkey(callback, "<ctrl>+<alt>+c")
    gerenciador.iniciar()
    mock_hotkeys_class.assert_called_once_with({"<ctrl>+<alt>+c": callback})


@patch("core.hotkey.GlobalHotKeys")
def test_iniciar_idempotente_nao_cria_segundo_listener(mock_hotkeys_class):
    gerenciador = GerenciadorHotkey(MagicMock())
    gerenciador.iniciar()
    gerenciador.iniciar()
    mock_hotkeys_class.assert_called_once()


# --- parar ---

@patch("core.hotkey.GlobalHotKeys")
def test_parar_chama_stop_no_listener(mock_hotkeys_class):
    mock_listener = MagicMock()
    mock_hotkeys_class.return_value = mock_listener
    gerenciador = GerenciadorHotkey(MagicMock())
    gerenciador.iniciar()
    gerenciador.parar()
    mock_listener.stop.assert_called_once()


@patch("core.hotkey.GlobalHotKeys")
def test_parar_limpa_referencia_ao_listener(mock_hotkeys_class):
    gerenciador = GerenciadorHotkey(MagicMock())
    gerenciador.iniciar()
    gerenciador.parar()
    assert gerenciador._listener is None


def test_parar_sem_listener_nao_levanta_excecao():
    GerenciadorHotkey(MagicMock()).parar()


# --- trocar_combinacao ---

@patch("core.hotkey.GlobalHotKeys")
def test_trocar_combinacao_recria_listener(mock_hotkeys_class):
    mock_listener = MagicMock()
    mock_hotkeys_class.return_value = mock_listener
    gerenciador = GerenciadorHotkey(MagicMock())
    gerenciador.iniciar()
    gerenciador.trocar_combinacao("<ctrl>+<alt>+h")
    assert mock_hotkeys_class.call_count == 2


@patch("core.hotkey.GlobalHotKeys")
def test_trocar_combinacao_usa_nova_combinacao(mock_hotkeys_class):
    gerenciador = GerenciadorHotkey(MagicMock())
    gerenciador.iniciar()
    gerenciador.trocar_combinacao("<ctrl>+<alt>+h")
    mapa = mock_hotkeys_class.call_args[0][0]
    assert "<ctrl>+<alt>+h" in mapa


@patch("core.hotkey.GlobalHotKeys")
def test_trocar_combinacao_para_listener_antigo(mock_hotkeys_class):
    mock_listener = MagicMock()
    mock_hotkeys_class.return_value = mock_listener
    gerenciador = GerenciadorHotkey(MagicMock())
    gerenciador.iniciar()
    gerenciador.trocar_combinacao("<ctrl>+<alt>+h")
    mock_listener.stop.assert_called_once()


@patch("core.hotkey.GlobalHotKeys")
def test_trocar_combinacao_atualiza_property(mock_hotkeys_class):
    gerenciador = GerenciadorHotkey(MagicMock())
    gerenciador.iniciar()
    gerenciador.trocar_combinacao("<ctrl>+<alt>+h")
    assert gerenciador.combinacao == "<ctrl>+<alt>+h"


# --- combinacao property ---

def test_combinacao_retorna_padrao_sem_iniciar():
    assert GerenciadorHotkey(MagicMock()).combinacao == COMBINACAO_PADRAO


def test_combinacao_retorna_valor_customizado():
    assert GerenciadorHotkey(MagicMock(), "<ctrl>+<alt>+x").combinacao == "<ctrl>+<alt>+x"
