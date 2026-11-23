"""
Animatik: vídeos animados com IA, no seu estilo.

  python main.py                       # liga o painel em http://localhost:8100
  python main.py criar roteiro.json --molde neon     # faz um vídeo direto de um roteiro (sem painel)
"""
import argparse
import json
import logging
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(RAIZ / "navegador"))  # o navegador do gravador fica aqui dentro
sys.path.insert(0, str(RAIZ))


def main():
    ap = argparse.ArgumentParser(description="Animatik")
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("iniciar", help="liga o painel")
    p.add_argument("--porta", type=int)
    c = sub.add_parser("criar", help="faz um vídeo a partir de um roteiro .json ou .txt")
    c.add_argument("roteiro")
    c.add_argument("--molde", default="neon")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    for barulhento in ("httpx", "httpcore", "uvicorn.access", "anthropic"):
        logging.getLogger(barulhento).setLevel(logging.WARNING)
    from animatik.util import carregar_config
    cfg = carregar_config()
    if a.cmd == "criar":
        from animatik.produzir import produzir
        from animatik.roteiro import roteiro_de_texto
        arq = Path(a.roteiro)
        rot = json.loads(arq.read_text(encoding="utf-8")) if arq.suffix == ".json" else roteiro_de_texto(arq.read_text(encoding="utf-8"))
        print("pronto:", produzir(rot, a.molde))
        return
    import uvicorn
    porta = (a.porta if a.cmd == "iniciar" and a.porta else None) or cfg.get("painel", {}).get("porta", 8100)
    print(f"\n  Animatik ligado. Abra no navegador:  http://localhost:{porta}\n  (para desligar, feche esta janela)\n")
    uvicorn.run("animatik.web:app", host="0.0.0.0", port=porta, log_level="warning")


if __name__ == "__main__":
    main()
