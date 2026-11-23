"""Coisas usadas em todo o Animatik."""
import json
import logging
import subprocess
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
WEB = RAIZ / "web"
MOLDES = RAIZ / "moldes"
SAIDA = RAIZ / "saida"
VIDEOS = SAIDA / "videos"

log = logging.getLogger("animatik")


def carregar_config() -> dict:
    with open(RAIZ / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def ler_json(caminho: Path, padrao=None):
    try:
        return json.loads(Path(caminho).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return padrao


def salvar_json(caminho: Path, dados) -> None:
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    tmp = caminho.with_suffix(caminho.suffix + ".tmp")
    tmp.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(caminho)


def duracao(arquivo: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(arquivo)],
                         capture_output=True, text=True).stdout.strip()
    try:
        return float(out.split()[0])
    except (ValueError, IndexError):
        return 0.0
