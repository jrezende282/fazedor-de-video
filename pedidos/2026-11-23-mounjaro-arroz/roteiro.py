"""Pedido: a Dona Cida, que comia um quilo de arroz por refeição, começa o Mounjaro e fica magrinha (com humor e final motivacional)."""
import json
import math
from pathlib import Path

TINTA = "#3a2716"
VESTIDO = "#c0504d"
VESTIDO2 = "#e6a08a"
CABELO = "#6b4428"
PELE = "#eab58c"
ARROZ = "#fbf8ee"
VERDE = "#5b8a3a"
VERDE2 = "#86b04a"
AMAR = "#f0b73a"
VERM = "#b4402a"
ROSA2 = "#f6c6d4"
CEU = "#bcd6d8"
ESTILO = f'stroke="{TINTA}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"'


def svg(corpo, vb="0 0 1000 900"):
    return f'<svg viewBox="{vb}" xmlns="http://www.w3.org/2000/svg"><g {ESTILO}>{corpo}</g></svg>'


def chao(y=820):
    return f'<path d="M0 {y} q250 -16 500 0 t500 0" fill="none" stroke-width="7"/>'


def texto(x, y, t, tam=64, cor=VERM, extra=""):
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Caveat" font-size="{tam}" fill="{cor}" stroke="none" {extra}>{t}</text>'


def brilho(x, y, r=26, extra=""):
    return (f'<path d="M{x} {y - r} q{r * .25} {r * .75} {r} {r} q-{r * .75} {r * .25} -{r} {r} q-{r * .25} -{r * .75} -{r} -{r} '
            f'q{r * .75} -{r * .25} {r} -{r}z" fill="{AMAR}" stroke-width="4" {extra}/>')


def coracao(x, y, s=1.0, cor=VERM, extra=""):
    return (f'<g {extra}><g transform="translate({x} {y}) scale({s})"><path d="M0 60 c-90 -60 -110 -120 -60 -150 c30 -18 55 0 60 25 '
            f'c5 -25 30 -43 60 -25 c50 30 30 90 -60 150z" fill="{cor}" stroke-width="{6 / s:.1f}"/></g></g>')


def cida(cx, pes, s=1.0, larg=1.0, rosto="feliz", bracos="baixo", extra=""):
    """Dona Cida. (cx, pes) = meio dos pés no chão. larg = 1.0 (antes) ... 0.45 (magrinha)."""
    cy = pes - 330 * s          # centro da cabeça
    r = 46 * s
    w = 150 * s * larg          # meia largura do vestido
    corpo_top = cy + r - 6 * s
    vestido = (f'<ellipse cx="{cx}" cy="{corpo_top + 120 * s:.0f}" rx="{w:.0f}" ry="{125 * s:.0f}" fill="{VESTIDO}"/>'
               f'<path d="M{cx - w * .85:.0f} {corpo_top + 175 * s:.0f} q{w * .85:.0f} {30 * s:.0f} {w * 1.7:.0f} 0" stroke="{VESTIDO2}" stroke-width="{10 * s:.0f}" fill="none"/>'
               f'<path d="M{cx - 22 * s:.0f} {corpo_top + 2 * s:.0f} q{22 * s:.0f} {26 * s:.0f} {44 * s:.0f} 0" fill="{PELE}"/>')
    pernas = f'<path d="M{cx - 30 * s * max(larg, .6):.0f} {pes - 85 * s:.0f} v{85 * s:.0f} M{cx + 30 * s * max(larg, .6):.0f} {pes - 85 * s:.0f} v{85 * s:.0f}" stroke-width="{14 * s:.0f}"/>'
    if rosto == "feliz":
        olhos = f'<path d="M{cx - 24 * s} {cy} q9 -9 18 0 M{cx + 6 * s} {cy} q9 -9 18 0" fill="none"/>'
        boca = f'<path d="M{cx - 16 * s} {cy + 18 * s} q16 16 32 0" fill="#fff"/>'
    elif rosto == "chocada":
        olhos = (f'<circle cx="{cx - 15 * s}" cy="{cy}" r="8" fill="#fff"/><circle cx="{cx + 15 * s}" cy="{cy}" r="8" fill="#fff"/>'
                 f'<circle cx="{cx - 15 * s}" cy="{cy}" r="3.5" fill="{TINTA}" stroke="none"/><circle cx="{cx + 15 * s}" cy="{cy}" r="3.5" fill="{TINTA}" stroke="none"/>')
        boca = f'<ellipse cx="{cx}" cy="{cy + 24 * s}" rx="10" ry="13" fill="#fff"/>'
    else:  # conformada
        olhos = f'<path d="M{cx - 24 * s} {cy + 2 * s} h18 M{cx + 6 * s} {cy + 2 * s} h18" fill="none"/>'
        boca = f'<path d="M{cx - 14 * s} {cy + 22 * s} h28" fill="none"/>'
    bochechas = (f'<circle cx="{cx - 30 * s}" cy="{cy + 14 * s}" r="{8 * s}" fill="{ROSA2}" stroke="none"/>'
                 f'<circle cx="{cx + 30 * s}" cy="{cy + 14 * s}" r="{8 * s}" fill="{ROSA2}" stroke="none"/>')
    ombro = w * .8
    if bracos == "alto":
        br = f'<path d="M{cx - ombro:.0f} {corpo_top + 30 * s:.0f} l-{60 * s:.0f} -{100 * s:.0f} M{cx + ombro:.0f} {corpo_top + 30 * s:.0f} l{60 * s:.0f} -{100 * s:.0f}" stroke-width="{14 * s:.0f}" fill="none"/>'
    elif bracos == "joinha":
        br = (f'<path d="M{cx - ombro:.0f} {corpo_top + 30 * s:.0f} l-{30 * s:.0f} {110 * s:.0f} M{cx + ombro:.0f} {corpo_top + 30 * s:.0f} l{70 * s:.0f} -{40 * s:.0f}" stroke-width="{14 * s:.0f}" fill="none"/>'
              f'<path d="M{cx + ombro + 70 * s:.0f} {corpo_top - 10 * s:.0f} v-{36 * s:.0f}" stroke-width="{12 * s:.0f}" fill="none"/>')
    else:
        br = f'<path d="M{cx - ombro:.0f} {corpo_top + 30 * s:.0f} q-{40 * s:.0f} {60 * s:.0f} -{20 * s:.0f} {110 * s:.0f} M{cx + ombro:.0f} {corpo_top + 30 * s:.0f} q{40 * s:.0f} {60 * s:.0f} {20 * s:.0f} {110 * s:.0f}" stroke-width="{14 * s:.0f}" fill="none"/>'
    coque = (f'<circle cx="{cx}" cy="{cy - 58 * s}" r="{26 * s}" fill="{CABELO}"/>'
             f'<path d="M{cx - 48 * s} {cy - 4 * s} q{4 * s} -{56 * s} {48 * s} -{56 * s} q{44 * s} 0 {48 * s} {56 * s}" fill="{CABELO}"/>')
    return (f'<g {extra}>{pernas}{vestido}{br}<circle cx="{cx}" cy="{cy}" r="{r}" fill="{PELE}"/>'
            f'{bochechas}{olhos}{boca}{coque}</g>')


def prato(cx, cy, rx=170, extra=""):
    return (f'<g {extra}><ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{rx * .32:.0f}" fill="#fff"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx * .72:.0f}" ry="{rx * .22:.0f}" fill="none" stroke-width="3"/></g>')


def montanha_arroz(cx, base, larg, alt, extra=""):
    graos = "".join(f'<ellipse cx="{cx + (k * 37 % int(larg)) - larg / 2 + 10:.0f}" cy="{base - (k * 53 % int(alt * .8)) - 20:.0f}" rx="7" ry="3.5" '
                    f'fill="none" stroke-width="2.5" transform="rotate({k * 41 % 180} {cx + (k * 37 % int(larg)) - larg / 2 + 10:.0f} {base - (k * 53 % int(alt * .8)) - 20:.0f})"/>'
                    for k in range(int(larg * alt / 3500)))
    return (f'<g {extra}><path d="M{cx - larg / 2:.0f} {base} q{larg * .15:.0f} -{alt:.0f} {larg / 2:.0f} -{alt:.0f} '
            f'q{larg * .35:.0f} 0 {larg / 2:.0f} {alt:.0f}z" fill="{ARROZ}"/>{graos}</g>')


def caneta(x, y, ang=-30, extra=""):
    """Caneta de aplicação genérica (sem marca)."""
    return (f'<g {extra}><g transform="rotate({ang} {x} {y})">'
            f'<rect x="{x - 40}" y="{y - 160}" width="80" height="320" rx="38" fill="#e9eef2"/>'
            f'<rect x="{x - 40}" y="{y - 160}" width="80" height="90" rx="38" fill="#7aa6c9"/>'
            f'<rect x="{x - 18}" y="{y - 20}" width="36" height="60" rx="6" fill="{CEU}" stroke-width="4"/>'
            f'<path d="M{x - 30} {y + 160} h60 l-14 34 h-32z" fill="#7aa6c9"/></g></g>')


def alface(x, y, r=34, cor=VERDE2, extra=""):
    return (f'<g {extra}><path d="M{x - r} {y} q{r * .2} -{r * 1.3:.0f} {r} -{r * .8:.0f} q{r * .8:.0f} -{r * .5:.0f} {r} {r * .8:.0f} '
            f'q-{r} {r * .6:.0f} -{r * 2} 0z" fill="{cor}"/><path d="M{x} {y - 4} v-{r * .7:.0f}" stroke-width="3" fill="none"/></g>')


# ---------------------------------------------------------------- cenas
def cena1():
    """Dona Cida abraçada num saco de arroz, com coraçõezinhos."""
    saco = (f'<g data-entra="baixo" data-t="0.4" data-d="0.5"><path d="M560 820 q-30 -170 20 -260 l40 -30 h120 l40 30 q50 90 20 260z" fill="#efe3c4"/>'
            f'<path d="M610 530 q60 20 120 0" fill="none" stroke-width="5"/>'
            f'<text x="680" y="700" text-anchor="middle" font-family="Inter" font-weight="900" font-size="52" fill="{VERM}" stroke="none">ARROZ</text>'
            f'<text x="680" y="755" text-anchor="middle" font-family="Inter" font-weight="800" font-size="30" fill="{TINTA}" stroke="none">5 kg</text></g>')
    coracoes = "".join(coracao(x, y, .35, VERM, f'data-entra="pop" data-t="{t}" data-pulsa="0.08"') for x, y, t in [(560, 330, 0.9), (800, 300, 1.05), (690, 230, 1.2)])
    return svg(chao(820) + cida(380, 820, 1.1, 1.0, "feliz", "baixo", 'data-entra="pop" data-t="0" data-d="0.6"') + saco + coracoes,
               vb="100 160 820 690")


def cena2():
    """Uma montanha de arroz no prato: um quilo."""
    return svg(chao(840) + '<rect x="150" y="760" width="700" height="24" fill="#8a5f30"/>'
               + prato(500, 760, 300, 'data-entra="zoom" data-t="0"')
               + montanha_arroz(500, 755, 480, 420, 'data-entra="baixo" data-t="0.3" data-d="0.7" data-origem="50% 100%" data-som="pop"')
               + f'<g data-entra="pop" data-t="1.0" data-som="impacto"><rect x="690" y="250" width="200" height="110" rx="14" fill="{AMAR}"/>'
               + f'<text x="790" y="330" text-anchor="middle" font-family="Inter" font-weight="900" font-size="64" fill="{TINTA}" stroke="none">1 kg</text></g>'
               + f'<g data-entra="dir" data-t="0.6" data-d="0.5" data-balanca="8" data-origem="10% 100%"><path d="M180 520 l120 120" stroke-width="16"/>'
               + f'<ellipse cx="160" cy="500" rx="40" ry="26" fill="#cfd3d6" transform="rotate(45 160 500)"/></g>'
               + brilho(290, 300, 30, 'data-entra="pop" data-t="1.2" data-pulsa="0.1"'), vb="100 200 820 660")


def cena3():
    """Chega a caneta, dramática, e o arroz treme."""
    raios = "".join(f'<path d="M{500 + 230 * math.cos(math.radians(a)):.0f} {470 + 230 * math.sin(math.radians(a)):.0f} '
                    f'l{60 * math.cos(math.radians(a)):.0f} {60 * math.sin(math.radians(a)):.0f}" fill="none" stroke="{AMAR}" stroke-width="10" '
                    f'data-entra="desenha" data-t="0.7" data-d="0.3"/>' for a in range(0, 360, 30))
    return svg(raios + caneta(500, 450, -25, 'data-entra="cima" data-t="0.1" data-d="0.6" data-som="impacto" data-pulsa="0.03"')
               + cida(820, 840, .7, 1.0, "chocada", "alto", 'data-entra="dir" data-t="0.8" data-d="0.4"')
               + montanha_arroz(170, 840, 220, 160, 'data-entra="fade" data-t="0.2" data-balanca="4"')
               + texto(500, 170, "a caneta!", 80, VERM, 'data-entra="pop" data-t="1.0"'), vb="60 120 900 740")


def cena5():
    """Prato só de salada, um tiquinho de arroz, e ela conformada."""
    folhas = "".join(alface(380 + (k * 67) % 250, 690 - (k * 29) % 70, 40, [VERDE2, VERDE][k % 2], f'data-entra="pop" data-t="{0.25 + 0.08 * k:.2f}"')
                     for k in range(9))
    tomates = "".join(f'<circle cx="{420 + 70 * k}" cy="{650 + 20 * (k % 2)}" r="20" fill="{VERM}" data-entra="pop" data-t="{1.0 + 0.1 * k:.2f}"/>' for k in range(3))
    tiquinho = montanha_arroz(640, 715, 50, 26, 'data-entra="pop" data-t="1.3"') + texto(700, 600, "40 g", 54, TINTA, 'data-entra="pop" data-t="1.5"')
    return svg(chao(840) + '<rect x="200" y="740" width="600" height="24" fill="#8a5f30"/>' + prato(500, 720, 230) + folhas + tomates + tiquinho
               + cida(190, 840, .78, .9, "conformada", "baixo", 'data-entra="esq" data-t="0" data-d="0.4"')
               + '<g data-som="pop" data-t="0.25"></g>', vb="40 380 900 470")


def cena6():
    """A balança: o ponteiro vai descendo."""
    balanca = (f'<g data-entra="zoom" data-t="0" data-d="0.5"><rect x="260" y="380" width="480" height="420" rx="60" fill="#e9eef2"/>'
               f'<rect x="300" y="420" width="400" height="230" rx="20" fill="#fff"/>'
               + "".join(f'<path d="M{500 + 150 * math.cos(math.radians(a)):.0f} {640 + 150 * math.sin(math.radians(a)):.0f} '
                         f'l{18 * math.cos(math.radians(a)):.0f} {18 * math.sin(math.radians(a)):.0f}" stroke-width="4" fill="none"/>'
                         for a in range(200, 341, 20)) +
               f'<rect x="330" y="690" width="140" height="80" rx="20" fill="#cfd8de"/><rect x="530" y="690" width="140" height="80" rx="20" fill="#cfd8de"/></g>')
    ponteiro = (f'<g data-tomba="-95" data-tomba-t="0.6" data-origem="50% 100%">'
                f'<path d="M500 640 L500 480" stroke="{VERM}" stroke-width="10"/></g>'
                f'<circle cx="500" cy="640" r="14" fill="{TINTA}"/>')
    setas = "".join(f'<path d="M{150 + 700 * k} 380 v200 m-30 -30 l30 30 l30 -30" fill="none" stroke="{VERDE}" stroke-width="12" '
                    f'data-entra="desenha" data-t="{0.8 + 0.3 * k:.1f}" data-d="0.5"/>' for k in range(2))
    return svg(balanca + ponteiro + setas + texto(500, 330, "descendo...", 80, VERDE, 'data-entra="pop" data-t="1.0"')
               + '<g data-som="subida" data-som-d="1.2" data-t="0.6"></g>', vb="60 250 880 580")


def cena7():
    """Magrinha! Segurando a calça antiga, enorme, com brilhos."""
    calca = (f'<g data-entra="dir" data-t="0.5" data-d="0.5" data-balanca="4" data-origem="50% 0%">'
             f'<path d="M560 420 h320 l30 400 h-150 l-35 -260 l-35 260 h-150z" fill="#5a6f99"/>'
             f'<path d="M560 450 h320" stroke-width="5" fill="none"/></g>')
    brilhos = "".join(brilho(x, y, r, f'data-entra="pop" data-t="{t}" data-pulsa="0.1"') for x, y, r, t in [(220, 330, 32, 0.8), (450, 300, 26, 1.0), (180, 600, 22, 1.2)])
    return svg(chao(840) + cida(350, 840, 1.15, .42, "feliz", "alto", 'data-entra="pop" data-t="0" data-d="0.6" data-som="impacto"') + calca + brilhos
               + texto(720, 360, "a calça antiga!", 64, VERM, 'data-entra="pop" data-t="1.1"'), vb="100 200 860 660")


def cena8():
    """Final: coração, ela fazendo joinha e a mensagem."""
    confete = "".join(f'<rect x="{150 + (k * 61) % 700}" y="{170 + (k * 37) % 160}" width="18" height="10" fill="{[VERDE2, AMAR, VERM, CEU][k % 4]}" stroke="none" '
                      f'data-entra="cai" data-t="{0.3 + 0.04 * k:.2f}" data-d="0.7"/>' for k in range(22))
    return svg(chao(840) + coracao(500, 470, 2.6, ROSA2, 'data-entra="zoom" data-t="0" data-d="0.5" data-pulsa="0.04"') + confete
               + cida(500, 840, 1.0, .45, "feliz", "joinha", 'data-entra="pop" data-t="0.15" data-d="0.6"')
               + texto(500, 150, "tudo vai dar certo", 80, VERM, 'data-entra="pop" data-t="1.0"')
               + '<g data-som="impacto" data-t="0.15"></g>', vb="100 90 800 780")


CENAS = [
    {"fala": "Essa é a Dona Cida, e ela era apaixonada por *arroz*.", "visual": {"tipo": "ilustracao", "svg": cena1()}},
    {"fala": "Era um *quilo* de arroz em cada refeição.", "visual": {"tipo": "ilustracao", "svg": cena2()}},
    {"fala": "Até que um belo dia... chegou o *Mounjaro*.", "visual": {"tipo": "ilustracao", "svg": cena3()}, "pausa": 0.4},
    {"fala": "Agora são quarenta *gramas* de arroz. Contadinhas.", "visual": {"tipo": "numero", "valor": "40", "sufixo": "g", "rotulo": "de arroz"}},
    {"fala": "E o resto do prato? *Salada*, salada e mais salada.", "visual": {"tipo": "ilustracao", "svg": cena5()}},
    {"fala": "Mas a balança foi *descendo*, descendo...", "visual": {"tipo": "ilustracao", "svg": cena6()}},
    {"fala": "E olha ela aí: *magrinha*!", "visual": {"tipo": "ilustracao", "svg": cena7()}},
    {"fala": "Continua firme no seu Mounjaro, com acompanhamento médico, que *tudo vai dar certo*!", "visual": {"tipo": "ilustracao", "svg": cena8()}},
]

roteiro = {"titulo": "Dona Cida e o Mounjaro",
           "legenda_post": "De um quilo de arroz para quarenta gramas 🍚➡️🥗 Continua firme, que tudo vai dar certo! 💪 #mounjaro #emagrecimento #antesedepois #motivacao #humor",
           "cenas": CENAS}
Path(__file__).with_name("roteiro.json").write_text(json.dumps(roteiro, ensure_ascii=False), encoding="utf-8")
print("ok", len(CENAS), "cenas")
