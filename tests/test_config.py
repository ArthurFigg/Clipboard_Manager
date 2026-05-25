import json
from pathlib import Path

import pytest

from config import PADRAO, carregar, salvar


# --- carregar ---

def test_carregar_retorna_padrao_se_arquivo_nao_existe(tmp_path):
    cam = tmp_path / "config.json"
    resultado = carregar(cam)
    assert resultado == PADRAO


def test_carregar_cria_arquivo_se_nao_existe(tmp_path):
    cam = tmp_path / "config.json"
    carregar(cam)
    assert cam.exists()


def test_carregar_arquivo_criado_e_json_valido(tmp_path):
    cam = tmp_path / "config.json"
    carregar(cam)
    dados = json.loads(cam.read_text(encoding="utf-8"))
    assert isinstance(dados, dict)


def test_carregar_le_arquivo_existente(tmp_path):
    cam = tmp_path / "config.json"
    config_salvo = {**PADRAO, "hotkey": "<ctrl>+<alt>+v"}
    salvar(config_salvo, cam)
    resultado = carregar(cam)
    assert resultado["hotkey"] == "<ctrl>+<alt>+v"


def test_carregar_preenche_chaves_ausentes_com_padrao(tmp_path):
    cam = tmp_path / "config.json"
    # Arquivo com apenas uma chave
    cam.write_text('{"hotkey": "<ctrl>+<alt>+v"}', encoding="utf-8")
    resultado = carregar(cam)
    assert "limite_historico" in resultado
    assert resultado["limite_historico"] == PADRAO["limite_historico"]


def test_carregar_retorna_padrao_em_json_invalido(tmp_path):
    cam = tmp_path / "config.json"
    cam.write_text("{ isso não é json }", encoding="utf-8")
    resultado = carregar(cam)
    assert resultado == PADRAO


def test_carregar_retorna_padrao_em_arquivo_vazio(tmp_path):
    cam = tmp_path / "config.json"
    cam.write_text("", encoding="utf-8")
    resultado = carregar(cam)
    assert resultado == PADRAO


# --- salvar ---

def test_salvar_cria_arquivo_json_valido(tmp_path):
    cam = tmp_path / "config.json"
    salvar(PADRAO.copy(), cam)
    dados = json.loads(cam.read_text(encoding="utf-8"))
    assert dados == PADRAO


def test_salvar_cria_diretorio_se_nao_existir(tmp_path):
    cam = tmp_path / "subdir" / "config.json"
    salvar(PADRAO.copy(), cam)
    assert cam.exists()


def test_salvar_sobrescreve_arquivo_existente(tmp_path):
    cam = tmp_path / "config.json"
    salvar({**PADRAO, "hotkey": "<ctrl>+<alt>+a"}, cam)
    salvar({**PADRAO, "hotkey": "<ctrl>+<alt>+b"}, cam)
    dados = json.loads(cam.read_text(encoding="utf-8"))
    assert dados["hotkey"] == "<ctrl>+<alt>+b"


# --- roundtrip ---

def test_salvar_e_carregar_preserva_valores(tmp_path):
    cam = tmp_path / "config.json"
    config_original = {**PADRAO, "hotkey": "<ctrl>+<shift>+x", "autostart": True}
    salvar(config_original, cam)
    assert carregar(cam) == config_original
