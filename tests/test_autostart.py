import sys
from unittest.mock import MagicMock, patch

from core import autostart


def _mock_open_key(mock_winreg):
    """Helper: configura OpenKey como context manager que retorna uma chave mock."""
    mock_chave = MagicMock()
    mock_winreg.OpenKey.return_value.__enter__ = MagicMock(return_value=mock_chave)
    mock_winreg.OpenKey.return_value.__exit__ = MagicMock(return_value=False)
    return mock_chave


# --- ativar ---

@patch("core.autostart.winreg")
def test_ativar_abre_chave_com_permissao_de_escrita(mock_winreg):
    _mock_open_key(mock_winreg)
    autostart.ativar("C:\\app.exe")
    mock_winreg.OpenKey.assert_called_once_with(
        mock_winreg.HKEY_CURRENT_USER,
        autostart._CHAVE_RUN,
        0,
        mock_winreg.KEY_SET_VALUE,
    )


@patch("core.autostart.winreg")
def test_ativar_registra_caminho_fornecido(mock_winreg):
    mock_chave = _mock_open_key(mock_winreg)
    autostart.ativar("C:\\meu_app.exe")
    mock_winreg.SetValueEx.assert_called_once_with(
        mock_chave, autostart._NOME_APP, 0, mock_winreg.REG_SZ, "C:\\meu_app.exe"
    )


@patch("core.autostart.winreg")
def test_ativar_usa_sys_executable_por_padrao(mock_winreg):
    _mock_open_key(mock_winreg)
    autostart.ativar()
    caminho_registrado = mock_winreg.SetValueEx.call_args[0][4]
    assert caminho_registrado == sys.executable


@patch("core.autostart.winreg")
def test_ativar_usa_nome_correto_do_app(mock_winreg):
    _mock_open_key(mock_winreg)
    autostart.ativar("C:\\app.exe")
    nome_usado = mock_winreg.SetValueEx.call_args[0][1]
    assert nome_usado == autostart._NOME_APP


# --- desativar ---

@patch("core.autostart.winreg")
def test_desativar_remove_valor_correto(mock_winreg):
    mock_chave = _mock_open_key(mock_winreg)
    autostart.desativar()
    mock_winreg.DeleteValue.assert_called_once_with(mock_chave, autostart._NOME_APP)


@patch("core.autostart.winreg")
def test_desativar_nao_falha_se_chave_nao_existe(mock_winreg):
    mock_winreg.OpenKey.side_effect = FileNotFoundError
    autostart.desativar()  # não deve lançar


@patch("core.autostart.winreg")
def test_desativar_nao_falha_se_valor_nao_existe(mock_winreg):
    _mock_open_key(mock_winreg)
    mock_winreg.DeleteValue.side_effect = FileNotFoundError
    autostart.desativar()  # não deve lançar


# --- esta_ativo ---

@patch("core.autostart.winreg")
def test_esta_ativo_retorna_true_quando_registrado(mock_winreg):
    mock_chave = _mock_open_key(mock_winreg)
    mock_winreg.QueryValueEx.return_value = ("C:\\app.exe", 1)
    assert autostart.esta_ativo() is True


@patch("core.autostart.winreg")
def test_esta_ativo_retorna_false_quando_chave_nao_existe(mock_winreg):
    mock_winreg.OpenKey.side_effect = FileNotFoundError
    assert autostart.esta_ativo() is False


@patch("core.autostart.winreg")
def test_esta_ativo_retorna_false_quando_valor_nao_existe(mock_winreg):
    _mock_open_key(mock_winreg)
    mock_winreg.QueryValueEx.side_effect = FileNotFoundError
    assert autostart.esta_ativo() is False


@patch("core.autostart.winreg")
def test_esta_ativo_abre_chave_com_permissao_de_leitura(mock_winreg):
    _mock_open_key(mock_winreg)
    mock_winreg.QueryValueEx.return_value = ("C:\\app.exe", 1)
    autostart.esta_ativo()
    mock_winreg.OpenKey.assert_called_once_with(
        mock_winreg.HKEY_CURRENT_USER,
        autostart._CHAVE_RUN,
        0,
        mock_winreg.KEY_READ,
    )
