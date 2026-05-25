import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_CAMINHO_PADRAO = (
    Path.home() / "AppData" / "Local" / "ClipboardManager" / "config.json"
)

PADRAO: dict = {
    "hotkey": "<ctrl>+<shift>+v",
    "limite_historico": 500,
    "autostart": False,
}


def carregar(caminho: Path | None = None) -> dict:
    """Carrega config do arquivo, preenchendo chaves ausentes com o padrão.

    Cria o arquivo com valores padrão na primeira execução.
    Retorna o padrão silenciosamente em caso de JSON inválido ou erro de I/O.
    """
    cam = caminho or _CAMINHO_PADRAO

    if not cam.exists():
        salvar(PADRAO.copy(), cam)
        return PADRAO.copy()

    try:
        with open(cam, encoding="utf-8") as f:
            dados = json.load(f)
        # Garante que novas chaves adicionadas ao padrão apareçam
        return {**PADRAO, **dados}
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Erro ao ler config (%s), usando padrão: %s", cam, e)
        return PADRAO.copy()


def salvar(config: dict, caminho: Path | None = None) -> None:
    """Persiste o config em disco."""
    cam = caminho or _CAMINHO_PADRAO
    cam.parent.mkdir(parents=True, exist_ok=True)
    with open(cam, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
