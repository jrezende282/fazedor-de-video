"""Pedido: a história da namorada (de patricinha a CLT com tendinite) e um final motivando a investir nos negócios com IA."""
import json
from pathlib import Path

TINTA = "#3a2716"
ROSA = "#e88aa6"
ROSA2 = "#f6c6d4"
AZUL = "#4a6fa5"
CABELO = "#5a3a22"
PELE = "#f0c39a"
CEU = "#bcd6d8"
AMAR = "#f0b73a"
VERM = "#b4402a"
VERDE = "#5b8a3a"
PAPEL = "#fbf6ea"
ESTILO = f'stroke="{TINTA}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"'


def svg(corpo, vb="0 0 1000 900"):
    return f'<svg viewBox="{vb}" xmlns="http://www.w3.org/2000/svg"><g {ESTILO}>{corpo}</g></svg>'


def chao(y=820):
    return f'<path d="M0 {y} q250 -16 500 0 t500 0" fill="none" stroke-width="7"/>'


def texto(x, y, t, tam=60, cor=VERM, extra=""):
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Caveat" font-size="{tam}" fill="{cor}" stroke="none" {extra}>{t}</text>'


def brilho(x, y, r=26, extra=""):
    return (f'<path d="M{x} {y - r} q{r * .25} {r * .75} {r} {r} q-{r * .75} {r * .25} -{r} {r} q-{r * .25} -{r * .75} -{r} -{r} '
            f'q{r * .75} -{r * .25} {r} -{r}z" fill="{AMAR}" stroke-width="4" {extra}/>')


def coracao(x, y, s=1.0, cor=VERM, extra=""):
    return (f'<g {extra}><g transform="translate({x} {y}) scale({s})"><path d="M0 60 c-90 -60 -110 -120 -60 -150 c30 -18 55 0 60 25 '
            f'c5 -25 30 -43 60 -25 c50 30 30 90 -60 150z" fill="{cor}" stroke-width="{6 / s:.1f}"/></g></g>')


def namorada(cx, cy, s=1.0, rosto="feliz", roupa="patricinha", bracos="baixo", extra=""):
    """A namorada: cabelo comprido castanho. (cx, cy) = centro da cabeça; os pés ficam em cy + 300*s."""
    r = 46 * s
    cabelo = f'<path d="M{cx - 58 * s} {cy + 90 * s} q-14 -150 {58 * s} -150 q{72 * s} 0 {58 * s} 150 q-{58 * s} 22 -{116 * s} 0z" fill="{CABELO}"/>'
    if rosto == "feliz":
        olhos = (f'<path d="M{cx - 24 * s} {cy} q9 -9 18 0 M{cx + 6 * s} {cy} q9 -9 18 0" fill="none"/>')
        boca = f'<path d="M{cx - 15 * s} {cy + 18 * s} q15 14 30 0" fill="#fff"/>'
    elif rosto == "cansada":
        olhos = (f'<path d="M{cx - 24 * s} {cy + 2 * s} h18 M{cx + 6 * s} {cy + 2 * s} h18" fill="none"/>'
                 f'<path d="M{cx - 24 * s} {cy + 12 * s} q9 6 18 0 M{cx + 6 * s} {cy + 12 * s} q9 6 18 0" fill="none" stroke="#9a7a9a" stroke-width="4"/>')
        boca = f'<path d="M{cx - 12 * s} {cy + 26 * s} q12 -8 24 0" fill="none"/>'
    elif rosto == "dormindo":
        olhos = f'<rect x="{cx - 32 * s}" y="{cy - 10 * s}" width="{64 * s}" height="{20 * s}" rx="8" fill="{ROSA}"/>'
        boca = f'<path d="M{cx - 8 * s} {cy + 22 * s} q8 5 16 0" fill="none"/>'
    else:  # assustada
        olhos = (f'<circle cx="{cx - 15 * s}" cy="{cy}" r="8" fill="#fff"/><circle cx="{cx + 15 * s}" cy="{cy}" r="8" fill="#fff"/>'
                 f'<circle cx="{cx - 15 * s}" cy="{cy}" r="3.5" fill="{TINTA}" stroke="none"/><circle cx="{cx + 15 * s}" cy="{cy}" r="3.5" fill="{TINTA}" stroke="none"/>')
        boca = f'<ellipse cx="{cx}" cy="{cy + 24 * s}" rx="9" ry="12" fill="#fff"/>'
    bochechas = (f'<circle cx="{cx - 28 * s}" cy="{cy + 14 * s}" r="{8 * s}" fill="{ROSA2}" stroke="none"/>'
                 f'<circle cx="{cx + 28 * s}" cy="{cy + 14 * s}" r="{8 * s}" fill="{ROSA2}" stroke="none"/>')
    topo = cy + r - 6 * s
    cor_blusa = ROSA if roupa == "patricinha" else AZUL
    blusa = f'<path d="M{cx - 52 * s} {topo + 120 * s} q-10 -100 {52 * s} -{110 * s} q{62 * s} 10 {52 * s} {110 * s}z" fill="{cor_blusa}"/>'
    if roupa == "patricinha":
        baixo = f'<path d="M{cx - 54 * s} {topo + 118 * s} h{108 * s} l{26 * s} {80 * s} h-{160 * s}z" fill="{ROSA2}"/>'
        extra_roupa = (f'<path d="M{cx - 38 * s} {cy - 34 * s} h{76 * s}" stroke-width="{12 * s}"/>'  # óculos na cabeça
                       f'<circle cx="{cx - 20 * s}" cy="{cy - 34 * s}" r="{13 * s}" fill="#2b241e"/><circle cx="{cx + 20 * s}" cy="{cy - 34 * s}" r="{13 * s}" fill="#2b241e"/>')
    else:
        baixo = f'<path d="M{cx - 50 * s} {topo + 118 * s} h{100 * s} l{6 * s} {80 * s} h-{112 * s}z" fill="#3b3f4a"/>'
        extra_roupa = (f'<path d="M{cx} {topo + 10 * s} v{40 * s}" stroke-width="3"/>'  # crachá
                       f'<rect x="{cx - 14 * s}" y="{topo + 50 * s}" width="{28 * s}" height="{36 * s}" rx="4" fill="#fff"/>')
    pernas = f'<path d="M{cx - 22 * s} {topo + 196 * s} v{80 * s} M{cx + 22 * s} {topo + 196 * s} v{80 * s}" stroke-width="{12 * s}"/>'
    if bracos == "alto":
        br = f'<path d="M{cx - 48 * s} {topo + 30 * s} l-{60 * s} -{90 * s} M{cx + 48 * s} {topo + 30 * s} l{60 * s} -{90 * s}" stroke-width="{13 * s}" fill="none"/>'
    elif bracos == "sacolas":
        br = (f'<path d="M{cx - 48 * s} {topo + 30 * s} l-{30 * s} {90 * s} M{cx + 48 * s} {topo + 30 * s} l{30 * s} {90 * s}" stroke-width="{13 * s}" fill="none"/>'
              f'<g data-balanca="5" data-origem="50% 0%"><path d="M{cx - 120 * s} {topo + 140 * s} h{80 * s} l-6 {90 * s} h-{68 * s}z" fill="{AMAR}"/>'
              f'<path d="M{cx - 100 * s} {topo + 140 * s} q20 -40 40 0" fill="none" stroke-width="4"/></g>'
              f'<g data-balanca="5" data-fase="1.5" data-origem="50% 0%"><path d="M{cx + 40 * s} {topo + 140 * s} h{84 * s} l-6 {94 * s} h-{72 * s}z" fill="{ROSA}"/>'
              f'<path d="M{cx + 62 * s} {topo + 140 * s} q20 -40 40 0" fill="none" stroke-width="4"/></g>')
    else:
        br = f'<path d="M{cx - 48 * s} {topo + 30 * s} l-{20 * s} {100 * s} M{cx + 48 * s} {topo + 30 * s} l{20 * s} {100 * s}" stroke-width="{13 * s}" fill="none"/>'
    return (f'<g {extra}>{cabelo}{pernas}{baixo}{blusa}{br}'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{PELE}"/>{bochechas}{olhos}{boca}{extra_roupa}'
            f'<path d="M{cx - 46 * s} {cy - 10 * s} q{20 * s} -{50 * s} {92 * s} 0" fill="{CABELO}"/></g>')


def relogio(cx, cy, r, hora, extra=""):
    import math
    ang = math.radians(hora * 30 - 90)
    return (f'<g {extra}><circle cx="{cx}" cy="{cy}" r="{r}" fill="{PAPEL}"/>'
            + "".join(f'<path d="M{cx + r * .8 * math.cos(math.radians(k * 30)):.0f} {cy + r * .8 * math.sin(math.radians(k * 30)):.0f} l0 0" stroke-width="8"/>' for k in range(12)) +
            f'<path d="M{cx} {cy} l{r * .5 * math.cos(ang):.0f} {r * .5 * math.sin(ang):.0f}" stroke-width="9"/>'
            f'<path d="M{cx} {cy} v-{r * .7:.0f}" stroke-width="5"/></g>')


# ---------------------------------------------------------------- cenas
def cena1():
    """A patricinha: óculos na cabeça, sacolas de compras e brilhos."""
    brilhos = "".join(brilho(x, y, r, f'data-entra="pop" data-t="{t}" data-pulsa="0.1"')
                      for x, y, r, t in [(250, 260, 34, 0.6), (760, 300, 28, 0.8), (700, 520, 22, 1.0), (300, 560, 24, 1.1)])
    return svg(chao(820) + brilhos + namorada(500, 470, 1.15, "feliz", "patricinha", "sacolas", 'data-entra="pop" data-t="0.1" data-d="0.6"')
               + texto(500, 250, "filhinha de papai", 68, VERM, 'data-entra="pop" data-t="1.3"'), vb="80 180 840 680")


def cena2():
    """Dormindo até uma da tarde... e fim de semana: festa."""
    cama = (f'<rect x="120" y="640" width="520" height="90" rx="20" fill="{ROSA2}"/>'
            f'<rect x="120" y="600" width="140" height="70" rx="20" fill="{PAPEL}"/>'
            f'<path d="M110 600 v220 M650 660 v160" stroke-width="12"/>')
    dorme = (f'<g transform="rotate(-90 230 600)">{namorada(230, 600, 0.6, "dormindo", "patricinha")}</g>')
    zzz = "".join(texto(330 + 40 * k, 560 - 40 * k, "z", 60 + 12 * k, TINTA, f'data-entra="fade" data-t="{0.2 + 0.25 * k:.2f}" data-mover="20,-40"') for k in range(3))
    rel = relogio(540, 360, 90, 1, 'data-entra="pop" data-t="0.3"') + texto(540, 500, "13h", 66, VERM, 'data-entra="pop" data-t="0.6"')
    baloes = "".join(f'<g data-entra="baixo" data-t="{1.3 + 0.12 * k:.2f}" data-d="0.7" data-balanca="4" data-fase="{k}">'
                     f'<ellipse cx="{760 + 70 * (k % 2)}" cy="{300 + 90 * k}" rx="48" ry="58" fill="{[ROSA, AMAR, CEU][k]}"/>'
                     f'<path d="M{760 + 70 * (k % 2)} {358 + 90 * k} q-10 60 10 120" fill="none" stroke-width="3"/></g>' for k in range(3))
    confete = "".join(f'<rect x="{700 + (k * 37) % 260}" y="{230 + (k * 53) % 120}" width="16" height="9" fill="{[ROSA, AMAR, VERDE, CEU][k % 4]}" stroke="none" '
                      f'data-entra="cai" data-t="{1.5 + 0.05 * k:.2f}" data-d="0.6"/>' for k in range(14))
    return svg(chao(820) + cama + dorme + zzz + rel + baloes + confete + texto(830, 250, "sextou!", 64, VERM, 'data-entra="pop" data-t="1.6"')
               + '<g data-som="pop" data-t="1.6"></g>', vb="80 190 900 660")


def cena3():
    """A carteira de trabalho levando o carimbo de CONTRATADA."""
    carteira = (f'<g data-entra="zoom" data-t="0" data-d="0.5"><rect x="250" y="180" width="440" height="600" rx="24" fill="#2f4f86"/>'
                f'<rect x="290" y="230" width="360" height="500" rx="10" fill="none" stroke="#c9b26a" stroke-width="4"/>'
                f'<text x="470" y="330" text-anchor="middle" font-family="Inter" font-weight="800" font-size="40" fill="#e8d9a0" stroke="none">CARTEIRA DE</text>'
                f'<text x="470" y="380" text-anchor="middle" font-family="Inter" font-weight="800" font-size="40" fill="#e8d9a0" stroke="none">TRABALHO</text></g>')
    carimbo = (f'<g data-entra="zoom" data-t="0.9" data-d="0.25" data-som="impacto"><g transform="rotate(-14 470 560)">'
               f'<rect x="270" y="500" width="400" height="120" rx="14" fill="none" stroke="{VERM}" stroke-width="12"/>'
               f'<text x="470" y="582" text-anchor="middle" font-family="Inter" font-weight="900" font-size="58" fill="{VERM}" stroke="none">CONTRATADA</text></g></g>')
    return svg(carteira + carimbo + namorada(860, 600, 0.55, "assustada", "patricinha", "alto", 'data-entra="dir" data-t="1.1" data-d="0.4"'),
               vb="180 140 780 700")


def cena4():
    """Despertador às seis, ônibus passando na janela e o computador o dia inteiro."""
    janela = (f'<rect x="80" y="180" width="330" height="240" fill="{CEU}"/>'
              f'<svg x="80" y="180" width="330" height="240" viewBox="80 180 330 240" overflow="hidden">'
              f'<g data-entra="fade" data-t="0.4" data-mover="-420,0"><rect x="420" y="300" width="230" height="100" rx="14" fill="{AMAR}"/>'
              f'<rect x="440" y="320" width="40" height="34" fill="{CEU}" stroke-width="4"/><rect x="495" y="320" width="40" height="34" fill="{CEU}" stroke-width="4"/>'
              f'<rect x="550" y="320" width="40" height="34" fill="{CEU}" stroke-width="4"/></g></svg>'
              f'<rect x="80" y="180" width="330" height="240" fill="none"/><path d="M245 180 v240 M80 300 h330" stroke-width="5"/>')
    mascara = ""
    despertador = (f'<g data-entra="pop" data-t="0" data-balanca="12" data-origem="50% 100%">{relogio(780, 300, 80, 6)}'
                   f'<path d="M710 230 l-30 -30 M850 230 l30 -30" stroke-width="12"/></g>'
                   + texto(905, 320, "6h", 70, VERM, 'data-entra="pop" data-t="0.3"'))
    mesa = (f'<rect x="100" y="640" width="800" height="30" fill="#8a5f30"/><path d="M140 670 v150 M860 670 v150" stroke-width="12"/>'
            f'<rect x="520" y="440" width="300" height="200" rx="10" fill="#2b241e"/><rect x="540" y="460" width="260" height="160" fill="{PAPEL}"/>'
            + "".join(f'<path d="M560 {490 + 26 * k} h{200 - 40 * (k % 3)}" stroke-width="5"/>' for k in range(5)) +
            f'<path d="M650 640 v-10 h40 v10" fill="#2b241e"/>')
    cafe = (f'<path d="M210 580 h80 v60 h-80z" fill="{PAPEL}"/><path d="M290 595 q30 10 0 30" fill="none"/>'
            + "".join(f'<path d="M{230 + 20 * k} 560 q-10 -20 0 -40" fill="none" stroke-width="4" data-entra="fade" data-t="{0.5 + 0.2 * k:.1f}" data-mover="0,-30"/>' for k in range(3)))
    return svg(janela + mascara + chao(820) + despertador + mesa + cafe
               + namorada(400, 500, 0.62, "cansada", "clt", "baixo", 'data-entra="baixo" data-t="0.2"')
               + '<g data-som="ding" data-t="0.05"></g>', vb="60 160 900 680")


def cena5():
    """Close no pulso: o braço doendo de tanto digitar, e a bolsa de gelo."""
    teclado = f'<rect x="120" y="620" width="760" height="130" rx="16" fill="#d8c29a"/>' + "".join(
        f'<rect x="{150 + 62 * (k % 11)}" y="{640 + 42 * (k // 11)}" width="48" height="32" rx="6" fill="{PAPEL}" stroke-width="3"/>' for k in range(22))
    braco = (f'<path d="M980 420 L560 560 q-40 14 -60 50 l-30 40 q-10 20 10 26 l120 -10 q40 -6 60 -30 L980 520z" fill="{PELE}"/>'
             f'<path d="M520 640 l-30 26 M545 645 l-26 30 M572 645 l-18 32" fill="none" stroke-width="10"/>')
    dor = "".join(f'<path d="M{620 + dx} {520 + dy} l{14 * sx} -{18} l{10 * sx} 14 l{14 * sx} -18" fill="none" stroke="{VERM}" stroke-width="7" '
                  f'data-entra="pop" data-t="{0.3 + 0.15 * k:.2f}" data-pulsa="0.12"/>' for k, (dx, dy, sx) in enumerate([(-40, -60, 1), (40, -80, 1), (-10, 110, 1), (90, 60, 1)]))
    gelo = (f'<g data-entra="cai" data-t="1.2" data-d="0.6" data-som="pop"><path d="M590 420 q70 -50 140 0 q20 60 -70 80 q-90 -20 -70 -80z" fill="#9fd0e8"/>'
            f'<path d="M640 410 l20 -40 l20 40" fill="none" stroke-width="5"/></g>')
    return svg(teclado + braco + dor + gelo + texto(330, 470, "ai, ai...", 76, VERM, 'data-entra="pop" data-t="0.6"'), vb="100 330 880 460")


def cena6():
    """A ideia: notebook com IA brilhando e uma lâmpada acesa em cima dela."""
    note = (f'<g data-entra="baixo" data-t="0.1"><path d="M520 520 h330 v210 h-330z" fill="#2b241e"/><rect x="540" y="540" width="290" height="170" fill="{PAPEL}"/>'
            f'<path d="M480 730 h410 l-30 30 h-350z" fill="#8f8a80"/></g>'
            f'<text x="685" y="640" text-anchor="middle" font-family="Inter" font-weight="900" font-size="70" fill="{AZUL}" stroke="none" data-entra="pop" data-t="0.6" data-pulsa="0.04">IA</text>'
            f'<path d="M560 690 l50 -30 l40 15 l60 -50 l50 20" fill="none" stroke="{VERDE}" stroke-width="6" data-entra="desenha" data-t="0.9" data-d="0.6"/>')
    lampada = (f'<g data-entra="pop" data-t="0.4" data-som="ding"><circle cx="300" cy="230" r="58" fill="#fff3b0"/>'
               f'<path d="M280 288 h40 v24 h-40z" fill="#8f8a80"/>'
               + "".join(f'<path d="M{300 + 80 * c:.0f} {230 + 80 * s_:.0f} l{20 * c:.0f} {20 * s_:.0f}" fill="none" stroke="{AMAR}" stroke-width="7" data-pulsa="0.1"/>'
                         for c, s_ in [(1, 0), (-1, 0), (0, -1), (.7, -.7), (-.7, -.7)]) + '</g>')
    return svg(chao(820) + note + lampada + brilho(870, 470, 26, 'data-entra="pop" data-t="1.1" data-pulsa="0.1"')
               + namorada(300, 540, 0.85, "feliz", "clt", "baixo", 'data-entra="esq" data-t="0" data-d="0.45"'), vb="120 150 820 700")


def cena8():
    """Final: ela de braços pra cima, coração e confete."""
    confete = "".join(f'<rect x="{150 + (k * 61) % 700}" y="{180 + (k * 37) % 160}" width="18" height="10" fill="{[ROSA, AMAR, VERDE, CEU][k % 4]}" stroke="none" '
                      f'data-entra="cai" data-t="{0.3 + 0.04 * k:.2f}" data-d="0.7"/>' for k in range(22))
    return svg(chao(820) + coracao(500, 450, 2.6, ROSA2, 'data-entra="zoom" data-t="0" data-d="0.5" data-pulsa="0.04"') + confete
               + namorada(500, 500, 0.95, "feliz", "clt", "alto", 'data-entra="pop" data-t="0.15" data-d="0.6"')
               + texto(500, 150, "eu acredito em você", 76, VERM, 'data-entra="pop" data-t="0.9"')
               + '<g data-som="impacto" data-t="0.15"></g>', vb="100 90 800 770")


CENAS = [
    {"fala": "Essa é a minha namorada, na época de *patricinha*.", "visual": {"tipo": "ilustracao", "svg": cena1()}},
    {"fala": "Acordava uma da tarde, e todo fim de semana tinha *festa*.", "visual": {"tipo": "ilustracao", "svg": cena2()}},
    {"fala": "Até que um dia... ela virou *CLT*.", "visual": {"tipo": "ilustracao", "svg": cena3()}, "pausa": 0.45},
    {"fala": "Agora é despertador às seis, ônibus e *computador* o dia inteiro.", "visual": {"tipo": "ilustracao", "svg": cena4()}},
    {"fala": "E o braço? *Tendinite* e túnel do carpo, de tanto digitar.", "visual": {"tipo": "ilustracao", "svg": cena5()}},
    {"fala": "Mas ela tem um plano: os negócios dela com *IA*.", "visual": {"tipo": "ilustracao", "svg": cena6()}},
    {"fala": "Cada passo que ela dá, fica mais perto de *sair* da CLT.", "visual": {"tipo": "fluxo", "itens": [
        {"rotulo": "CLT", "icone": "relogio"}, {"rotulo": "Negócios com IA", "icone": "ia"}, {"rotulo": "Liberdade", "icone": "foguete"}]}},
    {"fala": "Amor, eu acredito em você. Vai que vai *dar certo*!", "visual": {"tipo": "ilustracao", "svg": cena8()}},
]

roteiro = {"titulo": "De patricinha a dona do próprio negócio",
           "legenda_post": "De patricinha a CLT... e logo, dona do próprio negócio 💪✨ Amor, eu acredito em você! #clt #empreender #ia #motivacao #casal",
           "cenas": CENAS}
Path(__file__).with_name("roteiro.json").write_text(json.dumps(roteiro, ensure_ascii=False), encoding="utf-8")
print("ok", len(CENAS), "cenas")
