"""
Efeitos sonoros e música de fundo, gerados aqui mesmo (sem direitos autorais, nada baixado da internet).
- efeitos: transição (whoosh), pop, impacto, risco, digitação, subida, ding, check
- música: "pulso" (sintetizador escuro, combina com o neon) e "lofi" (piano suave, combina com o papel)
"""
import wave
from pathlib import Path

import numpy as np

TAXA = 44100


def _t(dur):
    return np.arange(int(dur * TAXA)) / TAXA


def _env(n, ataque=0.005, queda=0.2):
    t = np.arange(n) / TAXA
    return np.minimum(1, t / max(ataque, 1e-4)) * np.exp(-t / max(queda, 1e-4))


def _ruido(n, semente=0):
    return np.random.default_rng(semente).standard_normal(n)


def _passa_baixa(x, corte):
    a = np.exp(-2 * np.pi * corte / TAXA)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):  # filtro simples de 1 polo (sons são curtos)
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def efeito(nome: str, tom: int = 0, dur: float | None = None) -> np.ndarray:
    if nome == "transicao":  # whoosh: ruído que sobe e desce
        n = int(0.42 * TAXA)
        x = _ruido(n, 1)
        env = np.sin(np.linspace(0, np.pi, n)) ** 2
        y = np.diff(np.concatenate([[0], _passa_baixa(x, 2500)])) * 4 + _passa_baixa(x, 900) * 0.6
        return y * env * 0.35
    if nome == "pop":
        f = 520 * 2 ** (([0, 4, 7, 12, 16][tom % 5]) / 12)
        t = _t(0.12)
        freq = f * (1 + 0.6 * np.exp(-t * 60))
        return np.sin(2 * np.pi * np.cumsum(freq) / TAXA) * _env(len(t), 0.002, 0.035) * 0.45
    if nome == "check":
        f = 880 * 2 ** (([0, 3, 7, 12][tom % 4]) / 12)
        t = _t(0.16)
        return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * _env(len(t), 0.002, 0.05) * 0.3
    if nome == "impacto":
        t = _t(0.9)
        freq = 40 + 90 * np.exp(-t * 14)
        corpo = np.sin(2 * np.pi * np.cumsum(freq) / TAXA) * _env(len(t), 0.002, 0.28)
        estalo = _passa_baixa(_ruido(len(t), 2), 3000) * _env(len(t), 0.001, 0.03)
        return (corpo * 0.9 + estalo * 0.5) * 0.6
    if nome == "risco":
        n = int(0.3 * TAXA)
        x = np.diff(np.concatenate([[0], _ruido(n, 3)]))
        return x * _env(n, 0.01, 0.12) * 0.22
    if nome == "digitar":
        dur = dur or 1.0
        n = int(dur * TAXA)
        y = np.zeros(n)
        rnd = np.random.default_rng(4)
        pos = 0
        while pos < n - 2000:
            clique = np.diff(np.concatenate([[0], rnd.standard_normal(900)])) * _env(900, 0.0005, 0.004)
            y[pos:pos + 900] += clique * (0.12 + 0.08 * rnd.random())
            pos += int(TAXA * (0.055 + 0.05 * rnd.random()))
        return y
    if nome == "subida":
        dur = dur or 1.0
        t = _t(dur)
        freq = 300 + 900 * (t / dur) ** 2
        return np.sin(2 * np.pi * np.cumsum(freq) / TAXA) * np.minimum(1, t * 8) * (0.4 + 0.6 * t / dur) * 0.08
    if nome == "ding":
        t = _t(0.9)
        return (np.sin(2 * np.pi * 1318 * t) + 0.5 * np.sin(2 * np.pi * 1976 * t)) * _env(len(t), 0.002, 0.25) * 0.22
    if nome == "motor":  # máquina chegando: ronco grave que pulsa
        dur = dur or 2.0
        t = _t(dur)
        ronco = np.sin(2 * np.pi * 46 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 11 * t)) + 0.4 * np.sin(2 * np.pi * 92 * t)
        chiado = _passa_baixa(_ruido(len(t), 6), 400) * 0.6
        env = np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.5)
        return (ronco * 0.5 + chiado) * env * 0.22
    if nome == "graos":  # grãos caindo: chuvinha de estalos
        dur = dur or 1.5
        n = int(dur * TAXA)
        rnd = np.random.default_rng(8)
        y = np.zeros(n)
        for _ in range(int(dur * 260)):
            i = rnd.integers(0, max(1, n - 400))
            y[i:i + 400] += np.diff(np.concatenate([[0], rnd.standard_normal(400)])) * _env(400, 0.0003, 0.002) * rnd.uniform(0.03, 0.09)
        return y * np.minimum(1, np.arange(n) / (0.2 * TAXA)) * np.minimum(1, (n - np.arange(n)) / (0.3 * TAXA))
    return np.zeros(1)


def trilha_efeitos(eventos: list, duracao: float) -> np.ndarray:
    y = np.zeros(int((duracao + 1) * TAXA))
    for ev in eventos:
        s = efeito(ev["som"], int(ev.get("tom", 0)), ev.get("dur"))
        i = max(0, int(ev["t"] * TAXA))
        j = min(len(y), i + len(s))
        y[i:j] += s[: j - i]
    return y[: int(duracao * TAXA)]


# ------------------------------------------------------------------ música
NOTAS = {"A": 57, "B": 59, "C": 60, "D": 62, "E": 64, "F": 65, "G": 67}


def _hz(midi):
    return 440 * 2 ** ((midi - 69) / 12)


def _corda(freq: float, dur: float, brilho: float = 0.5, semente: int = 0) -> np.ndarray:
    """Corda dedilhada (Karplus-Strong): soa como violão."""
    n = int(dur * TAXA)
    p = max(2, int(TAXA / freq))
    buf = np.random.default_rng(semente).uniform(-1, 1, p)
    buf = _passa_baixa(buf, 1500 + 3000 * brilho)
    saida = np.empty(n)
    for i in range(0, n, p):  # um período por vez (rápido, sem laço por amostra)
        k = min(p, n - i)
        saida[i:i + k] = buf[:k]
        buf = 0.996 * 0.5 * (buf + np.roll(buf, -1))
    return saida * _env(n, 0.002, dur * 0.6)


def _violao(duracao: float, semente: int) -> np.ndarray:
    """Dedilhado de violão (G - D - Em - C), clima de interior."""
    y = np.zeros(int((duracao + 2) * TAXA))
    bpm = 92
    colcheia = 60 / bpm / 2
    acordes = [(43, [55, 59, 62, 67]), (38, [57, 62, 66, 69]), (40, [55, 59, 64, 67]), (36, [55, 60, 64, 67])]
    padrao = [0, 2, 1, 3, 2, 1, 3, 2]  # baixo, depois cordas de cima alternando
    rnd = np.random.default_rng(semente)
    k, t = 0, 0.0
    while t < duracao + 1:
        baixo, notas = acordes[(k // 8) % 4]
        i0 = int(t * TAXA)
        if k % 8 == 0:
            nota = _corda(_hz(baixo), 2.2, 0.3, k) * 0.35
        else:
            nota = _corda(_hz(notas[padrao[k % 8]]), 1.4, 0.55, k) * (0.16 + 0.05 * rnd.random())
        y[i0:i0 + len(nota)] += nota[: max(0, len(y) - i0)]
        k += 1
        t += colcheia * (1.04 if k % 2 else 0.96)  # leve balanço, menos "máquina"
    return y


def musica(estilo: str, duracao: float, semente: int = 1) -> np.ndarray:
    if estilo == "violao":
        y = _violao(duracao, semente)[: int(duracao * TAXA)]
        n = len(y)
        fade = np.ones(n)
        a, b = int(0.6 * TAXA), int(1.5 * TAXA)
        if n > a + b:
            fade[:a] = np.linspace(0, 1, a)
            fade[-b:] = np.linspace(1, 0, b)
        return y * fade
    rnd = np.random.default_rng(semente)
    y = np.zeros(int((duracao + 2) * TAXA))
    acordes = [("A", [0, 3, 7]), ("F", [0, 4, 7]), ("C", [0, 4, 7]), ("G", [0, 4, 7])]
    if estilo == "lofi":
        bpm, compasso = 80, 4
        acordes = [("D", [0, 3, 7, 10]), ("G", [0, 4, 7, 11]), ("C", [0, 4, 7, 11]), ("A", [0, 3, 7, 10])]
    else:
        bpm, compasso = 104, 4
    tempo = 60 / bpm
    barra = tempo * compasso
    k = 0
    while k * barra < duracao + 1:
        raiz_nome, intervalos = acordes[k % len(acordes)]
        raiz = NOTAS[raiz_nome] - (12 if estilo != "lofi" else 0)
        i0 = int(k * barra * TAXA)
        if estilo == "lofi":
            # piano suave (acorde dedilhado) + baixo + chimbal leve
            for j, iv in enumerate(intervalos):
                t = _t(barra * 1.2)
                f = _hz(raiz + iv)
                nota = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t))
                nota *= _env(len(t), 0.01, 0.9) * 0.07
                a = i0 + int(j * 0.06 * TAXA)
                y[a:a + len(nota)] += nota[: max(0, len(y) - a)]
            tb = _t(barra)
            baixo = np.sin(2 * np.pi * _hz(raiz - 24) * tb) * _env(len(tb), 0.02, 1.2) * 0.12
            y[i0:i0 + len(baixo)] += baixo[: max(0, len(y) - i0)]
            for b in range(compasso * 2):
                a = i0 + int(b * tempo / 2 * TAXA)
                n = 2200
                hat = np.diff(np.concatenate([[0], rnd.standard_normal(n)])) * _env(n, 0.001, 0.012) * (0.025 if b % 2 else 0.04)
                y[a:a + n] += hat[: max(0, len(y) - a)]
                if b % 4 == 0:
                    tk = _t(0.3)
                    kick = np.sin(2 * np.pi * np.cumsum(50 + 70 * np.exp(-tk * 30)) / TAXA) * _env(len(tk), 0.002, 0.12) * 0.22
                    y[a:a + len(kick)] += kick[: max(0, len(y) - a)]
        else:
            # pulso: baixo em colcheias + pad + batida discreta
            for b in range(compasso * 2):
                a = i0 + int(b * tempo / 2 * TAXA)
                tb = _t(tempo / 2)
                f = _hz(raiz - 12)
                serra = 2 * ((f * tb) % 1) - 1
                nota = _passa_baixa(serra, 500 + 300 * (b % 2)) * _env(len(tb), 0.003, 0.12) * 0.16
                y[a:a + len(nota)] += nota[: max(0, len(y) - a)]
                if b % 4 == 0:
                    tk = _t(0.35)
                    kick = np.sin(2 * np.pi * np.cumsum(45 + 90 * np.exp(-tk * 35)) / TAXA) * _env(len(tk), 0.002, 0.15) * 0.3
                    y[a:a + len(kick)] += kick[: max(0, len(y) - a)]
                if b % 4 == 2:
                    n = 4000
                    clap = _passa_baixa(rnd.standard_normal(n), 2500) * _env(n, 0.001, 0.03) * 0.08
                    y[a:a + n] += clap[: max(0, len(y) - a)]
            tp = _t(barra)
            pad = sum(np.sin(2 * np.pi * _hz(raiz + 12 + iv) * tp * (1 + d)) for iv in intervalos for d in (-0.003, 0.003))
            pad = pad * np.minimum(1, tp / 0.4) * np.minimum(1, (barra - tp) / 0.4) * 0.018
            y[i0:i0 + len(pad)] += pad[: max(0, len(y) - i0)]
        k += 1
    y = y[: int(duracao * TAXA)]
    n = len(y)
    fade = np.ones(n)
    a, b = int(0.8 * TAXA), int(1.5 * TAXA)
    fade[:a] = np.linspace(0, 1, min(a, n))[:a]
    fade[-b:] = np.linspace(1, 0, min(b, n))[-b:] if n > b else fade[-b:]
    return y * fade


def salvar_wav(y: np.ndarray, destino: Path) -> Path:
    y = np.clip(y, -1, 1)
    with wave.open(str(destino), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(TAXA)
        w.writeframes((y * 32000).astype(np.int16).tobytes())
    return destino
