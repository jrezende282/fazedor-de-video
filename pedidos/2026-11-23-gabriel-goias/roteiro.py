"""Pedido: vídeo zoando o Gabriel (entregador nos EUA, torcedor do Goiás) no dia em que o Goiás foi eliminado."""
import json
import random
from pathlib import Path

TINTA = "#3a2716"
VERDE = "#2f8a3e"
BRANCO = "#fbf6ea"
CAIXA = "#c9965a"
VERM = "#b4402a"
PELE = "#e0a978"
CEU = "#bcd6d8"
AMAR = "#f0b73a"
rnd = random.Random(7)
ESTILO = f'stroke="{TINTA}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"'


def svg(corpo, vb="0 0 1000 900"):
    return f'<svg viewBox="{vb}" xmlns="http://www.w3.org/2000/svg"><g {ESTILO}>{corpo}</g></svg>'


def chao(y=820, x0=0, x1=1000):
    return f'<path d="M{x0} {y} q{(x1 - x0) / 4} -16 {(x1 - x0) / 2} 0 t{(x1 - x0) / 2} 0" fill="none" stroke-width="7"/>'


def sol(cx, cy, r=50):
    raios = "".join(f'<path d="M{cx + (r + 16) * c:.0f} {cy + (r + 16) * s:.0f} l{20 * c:.0f} {20 * s:.0f}" fill="none"/>'
                    for c, s in [(1, 0), (-1, 0), (0, 1), (0, -1), (.7, .7), (-.7, .7), (.7, -.7), (-.7, -.7)])
    return f'<g data-entra="zoom" data-t="0.1" data-pulsa="0.03"><circle cx="{cx}" cy="{cy}" r="{r}" fill="#f6d27a"/>{raios}</g>'


def caixa(x, y, w=110, h=85, extra=""):
    return (f'<g {extra}><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{CAIXA}"/>'
            f'<path d="M{x + w / 2} {y} v{h}" stroke="#8a5f30" stroke-width="5"/>'
            f'<path d="M{x + 10} {y + h - 18} h28" stroke="#8a5f30" stroke-width="4"/></g>')


def camisa(cx, topo, s):
    """Camisa listrada verde e branca (cores do Goiás, sem escudo)."""
    w, h = 120 * s, 150 * s
    x0 = cx - w / 2
    listras = "".join(f'<rect x="{x0 + w * f:.0f}" y="{topo + 8 * s:.0f}" width="{w * 0.14:.0f}" height="{h - 14 * s:.0f}" fill="{BRANCO}" stroke="none"/>'
                      for f in (0.16, 0.43, 0.70))
    return (f'<path d="M{x0:.0f} {topo + h:.0f} q-8 -{h * 0.7:.0f} {w * 0.18:.0f} -{h:.0f} h{w * 0.64:.0f} q{w * 0.26:.0f} {h * 0.3:.0f} {w * 0.18:.0f} {h:.0f}z" fill="{VERDE}"/>'
            f'{listras}<path d="M{x0:.0f} {topo + h:.0f} q-8 -{h * 0.7:.0f} {w * 0.18:.0f} -{h:.0f} h{w * 0.64:.0f} q{w * 0.26:.0f} {h * 0.3:.0f} {w * 0.18:.0f} {h:.0f}z" fill="none"/>')


def gabriel(cx, cy, s=1.0, rosto="feliz", segura="caixa", correndo=False, extra=""):
    """Gabriel: boné de entregador, camisa listrada verde e branca. (cx, cy) = centro da cabeça."""
    r = 44 * s
    topo = cy + r - 4 * s
    if rosto == "feliz":
        olhos = f'<circle cx="{cx - 15 * s}" cy="{cy}" r="4.5" fill="{TINTA}" stroke="none"/><circle cx="{cx + 15 * s}" cy="{cy}" r="4.5" fill="{TINTA}" stroke="none"/>'
        boca = f'<path d="M{cx - 14 * s} {cy + 16 * s} q14 12 28 0" fill="none"/>'
    elif rosto == "tenso":
        olhos = f'<circle cx="{cx - 15 * s}" cy="{cy}" r="7" fill="#fff"/><circle cx="{cx + 15 * s}" cy="{cy}" r="7" fill="#fff"/><circle cx="{cx - 15 * s}" cy="{cy}" r="3" fill="{TINTA}" stroke="none"/><circle cx="{cx + 15 * s}" cy="{cy}" r="3" fill="{TINTA}" stroke="none"/>'
        boca = f'<path d="M{cx - 12 * s} {cy + 20 * s} h24" fill="none"/>'
    else:  # triste
        olhos = f'<path d="M{cx - 22 * s} {cy - 4 * s} l12 6 M{cx + 22 * s} {cy - 4 * s} l-12 6" fill="none"/>'
        boca = f'<path d="M{cx - 14 * s} {cy + 22 * s} q14 -12 28 0" fill="none"/>'
    pernas = (f'<path d="M{cx - 25 * s} {topo + 150 * s} l-30 {90 * s} M{cx + 25 * s} {topo + 150 * s} l40 {80 * s}" stroke-width="14" fill="none"/>' if correndo else
              f'<path d="M{cx - 25 * s} {topo + 150 * s} v{95 * s} M{cx + 25 * s} {topo + 150 * s} v{95 * s}" stroke-width="14" fill="none"/>')
    bermuda = f'<path d="M{cx - 58 * s} {topo + 140 * s} h{116 * s} l-6 {45 * s} h-{104 * s}z" fill="#4a5a7a"/>'
    mao = ""
    if segura == "caixa":
        mao = caixa(cx - 70 * s, topo + 50 * s, 140 * s, 100 * s)
    elif segura == "celular":
        mao = (f'<path d="M{cx + 50 * s} {topo + 40 * s} l{50 * s} -{70 * s}" stroke-width="12" fill="none"/>'
               f'<rect x="{cx + 82 * s}" y="{topo - 85 * s}" width="{36 * s}" height="{62 * s}" rx="6" fill="#2b241e"/>'
               f'<rect x="{cx + 87 * s}" y="{topo - 78 * s}" width="{26 * s}" height="{44 * s}" fill="{VERDE}" stroke="none"/>')
    bone = (f'<path d="M{cx - 44 * s} {cy - 14 * s} q{44 * s} -{70 * s} {88 * s} 0z" fill="#7a4e26"/>'
            f'<path d="M{cx + 30 * s} {cy - 16 * s} h{48 * s}" stroke-width="10"/>')
    return (f'<g {extra}>{pernas}{bermuda}{camisa(cx, topo, s)}'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{PELE}"/>{olhos}{boca}{bone}{mao}</g>')


def casa(x, y, cor="#e8c9a0", porta=VERM):
    return (f'<path d="M{x} {y} v-150 l90 -80 l90 80 v150z" fill="{cor}"/>'
            f'<rect x="{x + 65}" y="{y - 90}" width="50" height="90" fill="{porta}"/>'
            f'<rect x="{x + 18}" y="{y - 125}" width="34" height="30" fill="{CEU}"/>')


def caixa_correio(x, y):
    return (f'<path d="M{x} {y} v-110" stroke-width="10"/>'
            f'<path d="M{x - 40} {y - 110} v-40 q40 -40 80 0 v40z" fill="#5d6f80"/>'
            f'<path d="M{x + 40} {y - 140} v-40 h22 v14 h-22" fill="{VERM}" data-balanca="8" data-origem="0% 100%"/>')


def van(x, y, s=1.0, aberta=False, extra=""):
    def P(px, py):
        return f"{x + px * s:.0f} {y + py * s:.0f}"
    return (f'<g {extra}><path d="M{P(0, -40)} V{y - 260 * s:.0f} H{x + 330 * s:.0f} L{x + 420 * s:.0f} {y - 160 * s:.0f} V{y - 40 * s:.0f}z" fill="#f2ede2"/>'
            f'<path d="M{P(340, -245)} L{P(405, -165)} H{x + 340 * s:.0f}z" fill="{CEU}"/>'
            f'<path d="M{P(20, -150)} h{280 * s:.0f}" stroke="{VERDE}" stroke-width="10"/>'
            f'<g data-girar="-220"><circle cx="{x + 90 * s:.0f}" cy="{y - 40 * s:.0f}" r="{42 * s:.0f}" fill="#2b241e"/><circle cx="{x + 90 * s:.0f}" cy="{y - 40 * s:.0f}" r="{14 * s:.0f}" fill="{AMAR}"/></g>'
            f'<g data-girar="-220"><circle cx="{x + 330 * s:.0f}" cy="{y - 40 * s:.0f}" r="{42 * s:.0f}" fill="#2b241e"/><circle cx="{x + 330 * s:.0f}" cy="{y - 40 * s:.0f}" r="{14 * s:.0f}" fill="{AMAR}"/></g></g>')


def texto(x, y, t, tam=56, cor=VERM, extra=""):
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Caveat" font-size="{tam}" fill="{cor}" stroke="none" {extra}>{t}</text>'


# ---------------------------------------------------------------- cenas
def cena1():
    """Rua de bairro americano: casinhas, caixa de correio, a van e o Gabriel com uma caixa."""
    return svg(sol(880, 170) + chao(820) +
               f'<g data-entra="baixo" data-t="0" data-d="0.5">{casa(40, 820)}{casa(640, 820, "#d9b98c", VERDE)}</g>'
               + f'<g data-entra="fade" data-t="0.2">{caixa_correio(560, 820)}</g>'
               + gabriel(370, 478, 1.2, "feliz", "caixa", extra='data-entra="pop" data-t="0.45" data-d="0.6"')
               + texto(370, 300, "entregador oficial", 66, TINTA, 'data-entra="pop" data-t="1.1"'), vb="0 120 1000 740")


def cena2():
    """Celular gigante passando o jogo do Goiás, AO VIVO."""
    cel = (f'<g data-entra="zoom" data-t="0" data-d="0.5"><rect x="300" y="120" width="400" height="700" rx="50" fill="#2b241e"/>'
           f'<rect x="330" y="190" width="340" height="560" rx="10" fill="#4f8a3a"/>'
           f'<path d="M330 470 h340 M500 190 v560" stroke="{BRANCO}" stroke-width="4" fill="none"/>'
           f'<circle cx="500" cy="470" r="60" fill="none" stroke="{BRANCO}" stroke-width="4"/>'
           f'<rect x="420" y="690" width="160" height="60" fill="none" stroke="{BRANCO}" stroke-width="4"/>'
           f'<rect x="420" y="190" width="160" height="60" fill="none" stroke="{BRANCO}" stroke-width="4"/></g>')
    bola = (f'<g data-entra="pop" data-t="0.5" data-mover="40,170"><circle cx="460" cy="330" r="26" fill="#fff"/>'
            f'<path d="M448 322 l12 -8 l12 8 l-4 14 h-16z" fill="{TINTA}" stroke-width="2"/></g>')
    ao_vivo = (f'<g data-entra="pop" data-t="0.8" data-pulsa="0.05"><rect x="350" y="210" width="130" height="44" rx="8" fill="{VERM}"/>'
               f'<text x="415" y="242" text-anchor="middle" font-family="Inter" font-weight="800" font-size="24" fill="#fff" stroke="none">AO VIVO</text></g>')
    placa = texto(500, 100, "jogo decisivo!", 64, VERM, 'data-entra="cima" data-t="0.3"')
    return svg(cel + bola + ao_vivo + placa, vb="80 40 840 800")


def cena3():
    """A van abarrotada: caixas despencando e o Gabriel pequenininho, suando."""
    pilhas = ""
    k = 0
    for col in range(4):
        for lin in range(4 + (col % 2)):
            x = 200 + col * 115 + rnd.randint(-8, 8)
            y = 520 - lin * 88
            pilhas += caixa(x, y, 108, 84, extra=f'data-entra="cai" data-t="{0.1 + 0.06 * k:.2f}" data-d="0.45"')
            k += 1
    gota = f'<path d="M820 560 q-12 22 0 32 q12 -10 0 -32z" fill="#8cc4e0" data-entra="cai" data-t="1.6" data-d="0.5"/>'
    return svg(van(150, 820, 1.25) + pilhas + chao(820) + gabriel(820, 650, 0.6, "tenso", "nada") + gota
               + texto(820, 520, "socorro!", 66, VERM, 'data-entra="pop" data-t="1.5"')
               + '<g data-som="pop" data-t="0.1"></g>', vb="100 150 860 700")


def cena4():
    """Três portas: ele vai deixando caixa em cada uma, sempre de olho no celular."""
    casas = "".join(f'<g data-entra="baixo" data-t="{0.05 * i:.2f}">{casa(40 + 320 * i, 820, ["#e8c9a0", "#d9b98c", "#e3d1a8"][i], [VERM, VERDE, "#5d6f80"][i])}</g>' for i in range(3))
    entregues = "".join(caixa(70 + 320 * i, 750, 80, 64, extra=f'data-entra="pop" data-t="{0.6 + 0.65 * i:.2f}" data-som="pop"') for i in range(3))
    vento = "".join(f'<path d="M{110 + k * 30} {640 + k * 40} h-90" fill="none" stroke-width="5" opacity=".6" data-entra="fade" data-t="0.3" data-mover="560,0"/>' for k in range(3))
    return svg(casas + chao(820) + entregues + vento
               + gabriel(170, 610, 0.75, "tenso", "celular", correndo=True, extra='data-entra="esq" data-t="0.1" data-d="0.4" data-mover="560,0"'),
               vb="0 220 1000 640")


def cena5():
    """O cachorro do vizinho recebendo a caixa, e o Gabriel nem aí, olhando o jogo."""
    rabo = f'<path d="M760 700 q60 -40 50 -110" fill="none" stroke-width="12" data-balanca="22" data-origem="0% 100%"/>'
    cao = (f'<g data-entra="pop" data-t="0.2">{rabo}<ellipse cx="680" cy="720" rx="110" ry="70" fill="#c98f4a"/>'
           f'<circle cx="600" cy="600" r="70" fill="#c98f4a"/><path d="M548 560 q-30 40 -6 80 M652 560 q30 40 6 80" fill="#8a5f30"/>'
           f'<circle cx="578" cy="595" r="7" fill="{TINTA}" stroke="none"/><circle cx="622" cy="595" r="7" fill="{TINTA}" stroke="none"/>'
           f'<ellipse cx="600" cy="625" rx="14" ry="10" fill="{TINTA}"/><path d="M640 780 v40 M720 780 v40" stroke-width="12"/></g>')
    caixa_cao = caixa(540, 650, 120, 90, extra='data-entra="cai" data-t="0.9" data-d="0.5" data-som="pop"')
    duvida = texto(600, 510, "?", 120, VERM, 'data-entra="pop" data-t="1.3"')
    return svg(chao(820) + cao + caixa_cao + duvida
               + gabriel(250, 578, 0.85, "feliz", "celular", extra='data-entra="esq" data-t="0" data-d="0.5"')
               + texto(250, 420, "nem viu", 70, TINTA, 'data-entra="pop" data-t="1.5"'), vb="60 330 880 530")


def cena7():
    """A corrida: o Gabriel voando com a caixa, e lá atrás um caracol listrado (o time)."""
    linha = (f'<g data-entra="fade" data-t="0"><path d="M880 820 v-260" stroke-width="8"/>'
             + "".join(f'<rect x="{880 + 26 * (k % 2)}" y="{560 + 26 * (k // 2)}" width="26" height="26" fill="{TINTA if (k + k // 2) % 2 else BRANCO}" stroke="none"/>' for k in range(8))
             + '</g>')
    caracol = (f'<g data-entra="fade" data-t="0.2" data-mover="40,0"><path d="M60 800 q60 -10 160 0 q20 0 30 -30 l-10 -30" fill="#b9a06a"/>'
               f'<path d="M232 742 l-6 -40 M246 742 l10 -38" fill="none" stroke-width="5"/>'
               f'<circle cx="140" cy="740" r="62" fill="{VERDE}"/>'
               f'<path d="M140 680 v120 M100 690 q-10 50 0 100 M180 690 q10 50 0 100" stroke="{BRANCO}" stroke-width="12" fill="none"/>'
               f'<circle cx="140" cy="740" r="62" fill="none"/></g>')
    poeira = "".join(f'<circle cx="{500 - 40 * k}" cy="{800 - 10 * k}" r="{14 + 6 * k}" fill="#d9cdb8" data-entra="fade" data-t="{0.3 + 0.1 * k:.2f}" data-mover="380,0"/>' for k in range(3))
    return svg(chao(820) + linha + caracol + poeira
               + gabriel(520, 560, 0.8, "feliz", "caixa", correndo=True, extra='data-entra="esq" data-t="0" data-d="0.35" data-mover="190,0" data-som="transicao"')
               + texto(150, 630, "o time", 66, VERM, 'data-entra="pop" data-t="1.0"')
               + texto(640, 420, "Gabriel", 66, TINTA, 'data-entra="pop" data-t="0.7"'), vb="20 330 960 520")


CENAS = [
    {"fala": "Esse é o *Gabriel*: mora nos Estados Unidos e vive entregando caixa.", "visual": {"tipo": "ilustracao", "svg": cena1()}},
    {"fala": "Semana passada, jogo decisivo do *Goiás*.", "visual": {"tipo": "ilustracao", "svg": cena2()}},
    {"fala": "E ele? Com uma van inteira de *caixas* pra entregar.", "visual": {"tipo": "ilustracao", "svg": cena3()}},
    {"fala": "Entrega uma caixa, olha o celular. Entrega outra, olha o *celular*.", "visual": {"tipo": "ilustracao", "svg": cena4()}},
    {"fala": "De tanto olhar o jogo, quase entregou a caixa pro *cachorro* do vizinho.", "visual": {"tipo": "ilustracao", "svg": cena5()}},
    {"fala": "Apito final... Goiás *eliminado*.", "visual": {"tipo": "titulo", "texto": "eliminado", "sub": "fim de jogo"}, "pausa": 0.5},
    {"fala": "Moral da história: o Gabriel *corre* mais que o time dele.", "visual": {"tipo": "ilustracao", "svg": cena7()}},
    {"fala": "Força, Gabriel! Comenta *GOIÁS* pra consolar ele.", "visual": {"tipo": "cta", "palavra": "GOIÁS", "rotulo": "COMENTA"}},
]

roteiro = {"titulo": "Gabriel, o entregador do Goiás",
           "legenda_post": "O Gabriel corre mais que o time dele 📦⚽💚 Força, Gabriel! #goias #entregador #futebol #zoeira #brasileirão",
           "cenas": CENAS}
Path(__file__).with_name("roteiro.json").write_text(json.dumps(roteiro, ensure_ascii=False), encoding="utf-8")
print("ok", len(CENAS), "cenas")
