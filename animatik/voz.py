"""
Narração com voz de IA grátis (vozes neurais da Microsoft, as mesmas do Edge) e o tempo de CADA palavra,
para o texto na tela aparecer junto com a fala.
"""
import asyncio
import difflib
import os
import re
import subprocess
import unicodedata
import wave
from pathlib import Path

import numpy as np

from .util import log

TAXA = 24000

VOZES = {  # as "Multilingual" falam português também e costumam soar mais naturais (algumas com sotaque leve)
    "pt-BR-AntonioNeural": "1 · Antônio (masculina)",
    "pt-BR-FranciscaNeural": "2 · Francisca (feminina)",
    "pt-BR-ThalitaMultilingualNeural": "3 · Thalita (feminina, jovem)",
    "en-US-AndrewMultilingualNeural": "4 · Andrew (masculina, calorosa)",
    "en-US-BrianMultilingualNeural": "5 · Brian (masculina, casual)",
    "en-US-AvaMultilingualNeural": "6 · Ava (feminina, expressiva)",
    "en-US-EmmaMultilingualNeural": "7 · Emma (feminina, animada)",
    "fr-FR-RemyMultilingualNeural": "8 · Rémy (masculina)",
    "fr-FR-VivienneMultilingualNeural": "9 · Vivienne (feminina)",
    "it-IT-GiuseppeMultilingualNeural": "10 · Giuseppe (masculina)",
}


def _norm(p: str) -> str:
    p = unicodedata.normalize("NFD", p.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in p if unicodedata.category(c) != "Mn"))


async def _falar(texto: str, voz: str, velocidade: str, destino: Path, tom: str = "+0Hz") -> list:
    import edge_tts
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or None
    com = edge_tts.Communicate(texto, voz, rate=velocidade, pitch=tom, boundary="WordBoundary", proxy=proxy)
    marcas = []
    with open(destino, "wb") as f:
        async for pedaco in com.stream():
            if pedaco["type"] == "audio":
                f.write(pedaco["data"])
            elif pedaco["type"] == "WordBoundary":
                ini = pedaco["offset"] / 1e7
                marcas.append({"t": pedaco["text"], "ini": ini, "fim": ini + pedaco["duration"] / 1e7})
    return marcas


def _uma_fala(texto: str, voz: str, velocidade: str, tom: str, pasta: Path, i: int) -> tuple[np.ndarray, list]:
    mp3 = pasta / f"_fala{i:02d}.mp3"
    for tentativa in range(3):
        try:
            marcas = asyncio.run(_falar(texto, voz, velocidade, mp3, tom))
            if mp3.exists() and mp3.stat().st_size > 500:
                break
        except Exception as e:  # a conexão com o serviço de voz pode falhar: tenta de novo
            log.warning("voz: tentativa %d falhou: %s", tentativa + 1, e)
            if tentativa == 2:
                raise RuntimeError(f"não consegui gerar a narração (sem internet?): {e}")
    bruto = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp3), "-f", "s16le", "-ac", "1", "-ar", str(TAXA), "-"],
                           capture_output=True).stdout
    mp3.unlink(missing_ok=True)
    audio = np.frombuffer(bruto, np.int16).astype(np.float32) / 32768
    # tira o silêncio do começo e do fim (as pausas entre frases são colocadas por nós)
    forte = np.flatnonzero(np.abs(audio) > 0.01)
    ini = max(0, forte[0] - int(0.03 * TAXA)) if len(forte) else 0
    fim = min(len(audio), forte[-1] + int(0.08 * TAXA)) if len(forte) else len(audio)
    corte = ini / TAXA
    marcas = [{**m, "ini": max(0.0, m["ini"] - corte), "fim": max(0.0, m["fim"] - corte)} for m in marcas]
    return audio[ini:fim], marcas


def narrar(falas: list[str], voz: str, velocidade: str, destino: Path, tom: str = "+0Hz",
           pausas: list[float] | None = None) -> list[list[dict]]:
    """Gera a narração FRASE POR FRASE (cada uma com a entonação certa) e junta com pausas naturais entre elas.
    Devolve, para cada fala, as palavras do roteiro com início e fim (segundos) no áudio final."""
    pedacos, todas_marcas, t = [], [], 0.0
    for i, f in enumerate(falas):
        audio, marcas = _uma_fala(f.strip(), voz, velocidade, tom, destino.parent, i)
        pausa = (pausas[i] if pausas and i < len(pausas) else None)
        if pausa is None:  # respiro maior depois de pergunta/reticências, menor no resto
            pausa = 0.42 if f.strip().endswith(("?", "...", "…")) else 0.24
        todas_marcas.append([{**m, "ini": m["ini"] + t, "fim": m["fim"] + t} for m in marcas])
        pedacos += [audio, np.zeros(int(pausa * TAXA), np.float32)]
        t += len(audio) / TAXA + pausa
    tudo = np.concatenate(pedacos) if pedacos else np.zeros(TAXA, np.float32)
    with wave.open(str(destino), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(TAXA)
        w.writeframes((np.clip(tudo, -1, 1) * 32767).astype(np.int16).tobytes())
    return [_alinhar(f, m) for f, m in zip(falas, todas_marcas)]


def _alinhar(fala: str, marcas: list) -> list[dict]:
    """Palavras do roteiro (com pontuação) com o tempo que a voz deu para cada uma."""
    palavras = [p for p in fala.split() if _norm(p)]
    a = [_norm(p) for p in palavras]
    b = [_norm(m["t"]) for m in marcas]
    tempos: list = [None] * len(palavras)
    for bloco in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(bloco.size):
            m = marcas[bloco.b + k]
            tempos[bloco.a + k] = (m["ini"], m["fim"])
    conhecidos = [i for i, t in enumerate(tempos) if t]
    if not conhecidos:
        ini0 = marcas[0]["ini"] if marcas else 0.0
        fim0 = marcas[-1]["fim"] if marcas else ini0 + 0.4 * len(palavras)
        passo = (fim0 - ini0) / max(1, len(palavras))
        tempos = [(ini0 + i * passo, ini0 + (i + 1) * passo) for i in range(len(palavras))]
    else:
        # palavras que a voz falou diferente (números, siglas): tempo estimado entre as vizinhas
        for i, t in enumerate(tempos):
            if t:
                continue
            ant = max((k for k in conhecidos if k < i), default=None)
            prox = min((k for k in conhecidos if k > i), default=None)
            ini = tempos[ant][1] if ant is not None else (tempos[prox][0] - 0.3 if prox is not None else 0.0)
            fim = tempos[prox][0] if prox is not None else ini + 0.4
            buraco = list(range(ant + 1 if ant is not None else 0, prox if prox is not None else len(tempos)))
            pos = buraco.index(i)
            passo = max(0.05, (fim - ini) / max(1, len(buraco)))
            tempos[i] = (ini + pos * passo, ini + (pos + 1) * passo)
    return [{"t": p, "ini": round(ini, 3), "fim": round(fim, 3)} for p, (ini, fim) in zip(palavras, tempos)]
