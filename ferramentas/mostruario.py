"""
Mostruário dos estilos: o mesmo desenho (um celular-foguete decolando) em cada estilo "est-*".
Gera saida/mostruario/mostruario.mp4 (um trecho por estilo, com música) e grade.jpg (uma foto de cada).

  python ferramentas/mostruario.py              # todos os estilos
  python ferramentas/mostruario.py est-pixel    # só alguns (para conferir)
"""
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from animatik import sons  # noqa: E402
from animatik.moldes import carregar_molde  # noqa: E402
from animatik.render import renderizar  # noqa: E402

DUR = 2.6
TINTA = "#3a2716"


def foguete() -> str:
    """Celular-foguete com coração na tela, chamas, fumaça e coraçõezinhos subindo."""
    fum = "".join(f'<circle cx="{c}" cy="{790 + (k % 2) * 10}" r="{r}" fill="#f2efe8" data-entra="zoom" data-t="{0.2 + 0.08 * k:.2f}" '
                  f'data-mover="{(-1 if c < 500 else 1) * 40},10"/>' for k, (c, r) in enumerate([(330, 60), (420, 74), (580, 74), (670, 60), (500, 70)]))
    coracoes = "".join(f'<path d="M{x} {y} c-20 -14 -26 -30 -14 -38 c8 -5 14 0 14 6 c0 -6 6 -11 14 -6 c12 8 6 24 -14 38z" fill="#e2557a" '
                       f'data-entra="pop" data-t="{t}" data-mover="0,-120"/>' for x, y, t in [(330, 330, 0.7), (700, 290, 0.9), (640, 200, 1.2)])
    corpo = (
        f'<g data-entra="baixo" data-t="0" data-d="0.5" data-mover="0,-150">'
        f'<path d="M500 760 q-34 40 0 110 q34 -70 0 -110z" fill="#f0b73a" data-pulsa="0.12" data-origem="50% 0%"/>'
        f'<path d="M500 760 q-18 26 0 70 q18 -44 0 -70z" fill="#fff3b0" data-pulsa="0.18" data-origem="50% 0%"/>'
        f'<path d="M405 640 l-70 90 l70 -10z" fill="#d9573b"/><path d="M595 640 l70 90 l-70 -10z" fill="#d9573b"/>'
        f'<rect x="400" y="380" width="200" height="380" rx="34" fill="#2b3245"/>'
        f'<rect x="420" y="410" width="160" height="300" rx="12" fill="#f4f1ea"/>'
        f'<rect x="440" y="440" width="120" height="70" rx="8" fill="#9fd0e8"/>'
        f'<path d="M500 600 c-30 -20 -40 -45 -22 -58 c12 -8 22 0 22 10 c0 -10 10 -18 22 -10 c18 13 8 38 -22 58z" fill="#e2557a"/>'
        f'<path d="M445 640 h110 M445 670 h70" fill="none" stroke-width="5"/>'
        f'<circle cx="500" cy="732" r="9" fill="#f4f1ea"/></g>'
    )
    return (f'<svg viewBox="200 130 600 760" xmlns="http://www.w3.org/2000/svg"><g stroke="{TINTA}" stroke-width="6" '
            f'stroke-linecap="round" stroke-linejoin="round">{fum}{corpo}{coracoes}</g></svg>')


def dados_do_estilo(nome: str, n: int) -> dict:
    m = carregar_molde(nome)
    titulo = m["nome"].split("·", 1)[-1].strip()
    palavras = [{"t": f"{n}.", "ini": 0.05, "fim": 0.3, "dest": True}] + [
        {"t": p, "ini": 0.1 + 0.08 * i, "fim": 0.4 + 0.08 * i, "dest": False} for i, p in enumerate(titulo.split())]
    cena = {"n": 1, "ini": 0.0, "fim": DUR, "fala": titulo, "palavras": palavras, "visual": {"tipo": "ilustracao", "svg": foguete()}}
    return {"largura": 1080, "altura": 1920, "fps": 30, "duracao": DUR, "molde": m, "cenas": [cena]}


def main():
    pedidos = sys.argv[1:] or sorted(p.name for p in (RAIZ / "moldes").iterdir() if p.name.startswith("est-"))
    ordem = {json.loads((RAIZ / "moldes" / p / "molde.json").read_text(encoding="utf-8"))["nome"]: p for p in pedidos}
    pasta = RAIZ / "saida" / "mostruario"
    pasta.mkdir(parents=True, exist_ok=True)
    clipes, fotos = [], []
    for i, nome_exib in enumerate(sorted(ordem), 1):
        nome = ordem[nome_exib]
        n = int(nome_exib.split("·")[0]) if "·" in nome_exib else i
        clipe = pasta / f"{nome}.mp4"
        renderizar(dados_do_estilo(nome, n), clipe)
        foto = pasta / f"{nome}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1.9", "-i", str(clipe), "-frames:v", "1", "-vf", "scale=270:-2", str(foto)])
        clipes.append(clipe)
        fotos.append(foto)
        print("ok", nome)
    # grade com uma foto de cada estilo
    col = min(8, len(fotos))
    ent = sum([["-i", str(f)] for f in fotos], [])
    lay = "|".join(f"{(k % col) * 270}_{(k // col) * 480}" for k in range(len(fotos)))
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ent, "-filter_complex",
                    "".join(f"[{k}]" for k in range(len(fotos))) + f"xstack=inputs={len(fotos)}:layout={lay}:fill=black" if len(fotos) > 1 else "null",
                    str(pasta / "grade.jpg")])
    # vídeo: todos os trechos em sequência + violão + "whoosh" em cada troca
    lista = pasta / "lista.txt"
    lista.write_text("".join(f"file '{c.name}'\n" for c in clipes), encoding="utf-8")
    mudo = pasta / "_mudo.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(mudo)], check=True)
    total = DUR * len(clipes)
    trilha = sons.musica("pulso", total) * 0.5 + sons.trilha_efeitos([{"t": DUR * k, "som": "transicao"} for k in range(1, len(clipes))]
                                                                      + [{"t": DUR * k + 0.05, "som": "pop"} for k in range(len(clipes))], total)
    wav = sons.salvar_wav(trilha / max(1e-6, abs(trilha).max()) * 0.8, pasta / "_som.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mudo), "-i", str(wav), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(pasta / "mostruario.mp4")], check=True)
    mudo.unlink(missing_ok=True)
    wav.unlink(missing_ok=True)
    print("pronto:", pasta / "mostruario.mp4")


if __name__ == "__main__":
    main()
