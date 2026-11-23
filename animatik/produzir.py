"""
Produção de um vídeo, do roteiro ao MP4:
  roteiro -> narração (com o tempo de cada palavra) -> animação gravada -> efeitos + música -> vídeo final.
Cada vídeo fica numa pasta própria em saida/videos/<id>/ com o roteiro, o áudio, o vídeo e o andamento.
"""
import re
import subprocess
import tempfile
import time
import uuid
from pathlib import Path

import numpy as np

from . import sons
from .moldes import carregar_molde
from .render import foto, renderizar
from .util import VIDEOS, duracao, ler_json, log, salvar_json
from .voz import narrar

ATRASO = 0.35       # silêncio antes da primeira fala
SEGURA_FIM = 1.6    # segundos que a última cena fica na tela depois da fala
LARG, ALT, FPS = 1080, 1920, 30


def novo_id(titulo: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", titulo.lower())[:32].strip("-") or "video"
    return f"{time.strftime('%Y%m%d-%H%M%S')}-{base}-{uuid.uuid4().hex[:4]}"


class Andamento:
    """Guarda o andamento no meta.json (o painel lê dali)."""

    def __init__(self, pasta: Path):
        self.pasta = pasta
        self.meta = ler_json(pasta / "meta.json", {}) or {}

    def __call__(self, etapa: str, fracao: float, **extra):
        self.meta.update({"etapa": etapa, "progresso": round(fracao, 3), "atualizado": time.time(), **extra})
        salvar_json(self.pasta / "meta.json", self.meta)


def _separar_destaques(fala: str, extra: list | None = None) -> tuple[str, list[bool]]:
    """'Isso é *código* puro.' -> ('Isso é código puro.', [F, F, T, F])"""
    limpa, flags, dentro = [], [], False
    extra = {re.sub(r"\W", "", e.lower()) for e in (extra or []) if e}
    for tok in fala.split():
        abre = tok.startswith("*") or (tok[:1] in "\"'(" and tok[1:2] == "*")
        fecha = tok.rstrip(".,!?:;…\"')").endswith("*")
        if abre:
            dentro = True
        sem = tok.replace("*", "")
        if not sem:
            continue
        limpa.append(sem)
        flags.append(dentro or re.sub(r"\W", "", sem.lower()) in extra)
        if fecha:
            dentro = False
    return " ".join(limpa), flags


def montar_dados(roteiro: dict, molde: dict, falas_tempo: list, dur_audio: float) -> dict:
    cenas = []
    n = len(roteiro["cenas"])
    for i, (c, palavras) in enumerate(zip(roteiro["cenas"], falas_tempo)):
        ini = 0.0 if i == 0 else max(0.0, palavras[0]["ini"] + ATRASO - 0.12) if palavras else None
        cenas.append({"n": i + 1, "ini": ini, "fala": c["fala_limpa"], "visual": c.get("visual") or {"tipo": "nada"},
                      "palavras": [{"t": p["t"], "ini": round(p["ini"] + ATRASO, 3), "fim": round(p["fim"] + ATRASO, 3),
                                    "dest": d} for p, d in zip(palavras, c["destaques"])]})
    # cena sem palavras (não deveria acontecer): começa logo depois da anterior
    for i, c in enumerate(cenas):
        if c["ini"] is None:
            c["ini"] = cenas[i - 1]["ini"] + 1.0
    fim_fala = dur_audio + ATRASO
    for i, c in enumerate(cenas):
        c["fim"] = cenas[i + 1]["ini"] if i + 1 < n else fim_fala + SEGURA_FIM
    ultimo = cenas[-1]
    if ultimo["visual"].get("tipo") == "cta":
        ultimo["fim"] = max(ultimo["fim"], ultimo["ini"] + 2.6)
    total = round(ultimo["fim"] + 0.1, 3)
    return {"largura": LARG, "altura": ALT, "fps": FPS, "duracao": total, "molde": molde, "cenas": cenas}


def _mixar(video_mudo: Path, voz: Path, efeitos_wav: Path, musica_wav: Path, destino: Path, dur: float, molde: dict):
    """Junta tudo: voz + efeitos + música (que abaixa quando tem fala), volume no padrão das redes (-14 LUFS)."""
    atraso_ms = int(ATRASO * 1000)
    vol_mus = float(molde.get("volume_musica", 0.5))
    def grafo(ajuste: str) -> str:
        return (
        f"[1:a]aresample=44100,adelay={atraso_ms}|{atraso_ms},apad,atrim=0:{dur:.3f},"
        "acompressor=threshold=0.1:ratio=3:attack=5:release=120:makeup=1.5,asplit=2[voz][chave];"
        f"[3:a]volume={vol_mus}[mus];"
        "[mus][chave]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=350[duck];"
        "[2:a]volume=0.9[ef];"
        f"[voz][duck][ef]amix=inputs=3:duration=first:normalize=0,{ajuste}aresample=48000[a]"
        )
    entradas = ["-i", str(video_mudo), "-i", str(voz), "-i", str(efeitos_wav), "-i", str(musica_wav)]
    # 1) mede o volume da mistura; 2) aplica o ganho exato + limitador (sai em -14 LUFS, sem estourar)
    def medir(ajuste: str) -> float | None:
        r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *entradas, "-filter_complex", grafo(ajuste + "ebur128,"),
                            "-map", "[a]", "-t", f"{dur:.3f}", "-f", "null", "-"], capture_output=True, text=True)
        achados = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
        return float(achados[-1]) if achados else None

    limitador = "alimiter=limit=0.76:attack=4:release=60:level=false,"
    ganho = 0.0
    nivel = medir("")
    if nivel is not None and nivel > -70:
        ganho = max(-20.0, min(20.0, -14.0 - nivel))
        for _ in range(3):  # o limitador "come" um pouco do volume: mede de novo e corrige
            novo = medir(f"volume={ganho:.2f}dB,{limitador}")
            if novo is None or abs(-14.0 - novo) < 0.4:
                break
            ganho = max(-20.0, min(24.0, ganho + (-14.0 - novo)))
    ajuste = f"volume={ganho:.2f}dB,{limitador}"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *entradas, "-filter_complex", grafo(ajuste),
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{dur:.3f}",
                    "-movflags", "+faststart", str(destino)], check=True)


def produzir(roteiro: dict, nome_molde: str, pasta: Path | None = None, voz: str | None = None) -> Path:
    """Faz o vídeo inteiro. Devolve o caminho do MP4."""
    molde = carregar_molde(nome_molde)
    pasta = pasta or VIDEOS / novo_id(roteiro.get("titulo", "video"))
    pasta.mkdir(parents=True, exist_ok=True)
    andamento = Andamento(pasta)
    andamento("roteiro", 0.02, titulo=roteiro.get("titulo", ""), molde=nome_molde, status="produzindo",
              criado=andamento.meta.get("criado") or time.time(), erro="")
    try:
        for c in roteiro["cenas"]:
            c["fala_limpa"], c["destaques"] = _separar_destaques(c["fala"], (c.get("visual") or {}).get("destaque_fala"))
        salvar_json(pasta / "roteiro.json", roteiro)

        andamento("narração", 0.06)
        audio = pasta / "voz.wav"
        falas_tempo = narrar([c["fala_limpa"] for c in roteiro["cenas"]], voz or molde.get("voz", "pt-BR-AntonioNeural"),
                             molde.get("velocidade", "+8%"), audio, tom=molde.get("tom_voz", "+0Hz"),
                             pausas=[c.get("pausa") for c in roteiro["cenas"]])
        dados = montar_dados(roteiro, molde, falas_tempo, duracao(audio))
        salvar_json(pasta / "cenas.json", dados)

        andamento("animação", 0.12)
        mudo = pasta / "_mudo.mp4"
        res = renderizar(dados, mudo, progresso=lambda f, s: andamento("animação", 0.12 + 0.78 * f))

        andamento("som", 0.92)
        dur = dados["duracao"]
        with tempfile.TemporaryDirectory(dir=pasta) as tmp:
            ef = sons.salvar_wav(sons.trilha_efeitos(res["sons"], dur), Path(tmp) / "efeitos.wav")
            mus = sons.musica(molde.get("musica", "pulso"), dur, semente=abs(hash(pasta.name)) % 1000)
            mus = sons.salvar_wav(mus * 0.9, Path(tmp) / "musica.wav")
            final = pasta / "video.mp4"
            _mixar(mudo, audio, ef, mus, final, dur, molde)
        mudo.unlink(missing_ok=True)
        # miniatura: um instante da 1ª cena, já com o título aparecendo
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{min(1.2, dur / 2):.2f}", "-i", str(final),
                        "-frames:v", "1", "-vf", "scale=360:-2", str(pasta / "miniatura.jpg")])
        andamento("pronto", 1.0, status="pronto", duracao=round(dur, 1), legenda_post=roteiro.get("legenda_post", ""))
        return final
    except Exception as e:
        log.exception("erro produzindo %s", pasta.name)
        andamento("erro", andamento.meta.get("progresso", 0), status="erro", erro=str(e)[:500])
        raise


def previa(roteiro: dict, nome_molde: str, destino: Path, cena: int = 0) -> Path:
    """Foto de uma cena (sem narração, com tempos estimados) para conferir o visual rápido."""
    molde = carregar_molde(nome_molde)
    t, falas = 0.0, []
    for c in roteiro["cenas"]:
        c["fala_limpa"], c["destaques"] = _separar_destaques(c["fala"])
        pal = []
        for p in c["fala_limpa"].split():
            pal.append({"t": p, "ini": t, "fim": t + 0.3})
            t += 0.32
        t += 0.3
        falas.append(pal)
    dados = montar_dados(roteiro, molde, falas, t)
    alvo = dados["cenas"][min(cena, len(dados["cenas"]) - 1)]
    return foto(dados, alvo["fim"] - 0.05, destino)
