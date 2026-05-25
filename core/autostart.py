import sys
import winreg

_CHAVE_RUN = r"Software\Microsoft\Windows\CurrentVersion\Run"
_NOME_APP = "ClipboardManager"


def ativar(caminho: str | None = None) -> None:
    """Registra o app para iniciar com o Windows.

    caminho: path do executável. Usa sys.executable por padrão — em produção
    deve receber o path do executável compilado ou do launcher.
    """
    executavel = caminho or sys.executable
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, _CHAVE_RUN, 0, winreg.KEY_SET_VALUE
    ) as chave:
        winreg.SetValueEx(chave, _NOME_APP, 0, winreg.REG_SZ, executavel)


def desativar() -> None:
    """Remove o app do autostart. Silencioso se já não estiver registrado."""
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _CHAVE_RUN, 0, winreg.KEY_SET_VALUE
        ) as chave:
            winreg.DeleteValue(chave, _NOME_APP)
    except FileNotFoundError:
        pass


def esta_ativo() -> bool:
    """Retorna True se o app está registrado para autostart."""
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _CHAVE_RUN, 0, winreg.KEY_READ
        ) as chave:
            winreg.QueryValueEx(chave, _NOME_APP)
            return True
    except FileNotFoundError:
        return False
