"""Pedido: vídeo para o feed do sogro, divulgando a ClaroFlex (cortina de vidro com sistema europeu sem roldanas).
Fatos usados (pesquisa): empresa espanhola; no sistema Pivot o painel não fica pendurado em roldanas, desliza numa pista
inferior de baixo atrito e o peso fica apoiado no chão; manutenção mínima; os painéis abrem para o lado."""
import json
from pathlib import Path

TINTA = "#2b3245"
VIDRO = "#bfe3f2"
ALUM = "#b9c2cc"
FERRUGEM = "#77736d"  # (era ferrugem; agora só sujeira cinza: ele pediu para não falar em ferrugem)
VERM = "#e3262f"  # vermelho da logo
PELE = "#e9b48a"
CAMISA = "#4a78b5"
AMAR = "#f0b73a"
VERDE = "#3fa86b"
CEU = "#ffd6a6"
ESTILO = f'stroke="{TINTA}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"'


def svg(corpo, vb="0 0 1000 900"):
    return f'<svg viewBox="{vb}" xmlns="http://www.w3.org/2000/svg"><g {ESTILO}>{corpo}</g></svg>'


def texto(x, y, t, tam=64, cor=VERM, extra="", fonte="Fredoka", peso=700):
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{fonte}" font-weight="{peso}" font-size="{tam}" '
            f'fill="{cor}" stroke="none" {extra}>{t}</text>')


def painel(x, y, w=170, h=440, extra=""):
    """Um painel de vidro com reflexo."""
    return (f'<g {extra}><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{VIDRO}" fill-opacity=".75"/>'
            f'<path d="M{x + w * .2} {y + 40} l{w * .35} -30 M{x + w * .2} {y + 90} l{w * .55} -50" fill="none" stroke="#ffffff" stroke-width="8" opacity=".8"/></g>')


def roldana(cx, cy, r=34, enferrujada=False, extra=""):
    manchas = "".join(f'<circle cx="{cx + dx}" cy="{cy + dy}" r="{rr}" fill="{FERRUGEM}" stroke="none"/>'
                      for dx, dy, rr in [(-14, -10, 9), (12, 8, 11), (4, -20, 6), (-6, 16, 7)]) if enferrujada else ""
    return (f'<g {extra}><circle cx="{cx}" cy="{cy}" r="{r}" fill="#8f97a1"/><circle cx="{cx}" cy="{cy}" r="{r * .35:.0f}" fill="#5d6570"/>'
            f'{manchas}</g>')


def pessoa(cx, pes, s=1.0, extra="", rosto="bravo", bracos="empurra"):
    cy = pes - 320 * s
    if rosto == "bravo":
        olhos = (f'<path d="M{cx - 24 * s} {cy - 8 * s} l16 6 M{cx + 24 * s} {cy - 8 * s} l-16 6" fill="none"/>'
                 f'<circle cx="{cx - 14 * s}" cy="{cy + 4 * s}" r="4" fill="{TINTA}" stroke="none"/><circle cx="{cx + 14 * s}" cy="{cy + 4 * s}" r="4" fill="{TINTA}" stroke="none"/>')
        boca = f'<path d="M{cx - 14 * s} {cy + 26 * s} q14 -10 28 0" fill="none"/>'
    else:
        olhos = f'<path d="M{cx - 24 * s} {cy} q9 -9 18 0 M{cx + 6 * s} {cy} q9 -9 18 0" fill="none"/>'
        boca = f'<path d="M{cx - 15 * s} {cy + 18 * s} q15 14 30 0" fill="#fff"/>'
    topo = cy + 42 * s
    br = (f'<path d="M{cx + 40 * s} {topo + 40 * s} l{110 * s} {10 * s} M{cx + 40 * s} {topo + 80 * s} l{110 * s} {10 * s}" stroke-width="{14 * s}" fill="none"/>'
          if bracos == "empurra" else
          f'<path d="M{cx - 44 * s} {topo + 30 * s} l-{50 * s} -{90 * s} M{cx + 44 * s} {topo + 30 * s} l{50 * s} -{90 * s}" stroke-width="{14 * s}" fill="none"/>')
    return (f'<g {extra}><path d="M{cx - 22 * s} {topo + 170 * s} v{105 * s} M{cx + 22 * s} {topo + 170 * s} v{105 * s}" stroke-width="{15 * s}" fill="none"/>'
            f'<path d="M{cx - 55 * s} {topo + 175 * s} q-6 -150 {55 * s} -160 q{61 * s} 10 {55 * s} 160z" fill="{CAMISA}"/>{br}'
            f'<circle cx="{cx}" cy="{cy}" r="{44 * s}" fill="{PELE}"/>{olhos}{boca}'
            f'<path d="M{cx - 44 * s} {cy - 8 * s} q{10 * s} -{50 * s} {44 * s} -{44 * s} q{40 * s} -{4 * s} {44 * s} {40 * s}" fill="#3a2a20"/></g>')


def trilho_cima(x0=100, x1=900, y=200):
    return f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="40" rx="8" fill="{ALUM}"/>'


def pista_baixo(x0=100, x1=900, y=700):
    return f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="30" rx="8" fill="{ALUM}"/><path d="M{x0} {y + 32} h{x1 - x0}" stroke-width="8" fill="none"/>'


def logo_claroflex() -> str:
    """Logo da ClaroFlex como na imagem enviada: fundo preto, retângulo vermelho vazado, CLAROFLEX em branco e ®."""
    return ('<svg viewBox="0 0 700 140" xmlns="http://www.w3.org/2000/svg">'
            '<rect width="700" height="140" fill="#0d0d0d"/>'
            '<rect x="40" y="44" width="118" height="54" rx="4" fill="none" stroke="#e3262f" stroke-width="10"/>'
            '<text x="184" y="96" font-family="Inter" font-weight="400" font-size="66" letter-spacing="3" fill="#ffffff">CLAROFLEX</text>'
            '<text x="652" y="58" font-family="Inter" font-weight="400" font-size="20" fill="#ffffff">®</text></svg>')


# ---------------------------------------------------------------- cenas
def cena1():
    """Gancho: a pessoa empurrando o vidro emperrado, que treme. TRAVOU!"""
    return svg(trilho_cima(250, 900, 180) + pista_baixo(250, 900, 680)
               + painel(560, 220, 190, 460, 'data-balanca="2.5" data-origem="50% 0%"')
               + pessoa(390, 800, 1.25, 'data-entra="esq" data-t="0" data-d="0.4"')
               + "".join(f'<path d="M{770 + 18 * k} {300 + 60 * k} l40 -14" stroke="{VERM}" stroke-width="7" fill="none" data-entra="pop" data-t="{0.4 + 0.1 * k:.1f}" data-pulsa="0.15"/>' for k in range(3))
               + texto(640, 150, "TRAVOU!", 92, VERM, 'data-entra="pop" data-t="0.7" data-som="impacto"'), vb="150 60 830 760")


def cena2():
    """O culpado lá em cima: as roldanas, uma enferrujada e cheia de sujeira."""
    lupa = (f'<g data-entra="zoom" data-t="0.5" data-d="0.5"><circle cx="640" cy="330" r="170" fill="#ffffff" fill-opacity=".35" stroke-width="12"/>'
            f'<path d="M760 450 l120 120" stroke-width="30" fill="none"/></g>')
    return svg(trilho_cima(100, 900, 200) + roldana(330, 260, 40, False) + roldana(640, 260, 44, True, 'data-entra="pop" data-t="0.3"')
               + painel(270, 290, 150, 380) + painel(580, 290, 150, 380)
               + "".join(f'<circle cx="{600 + 26 * k}" cy="{320 + (k % 2) * 16}" r="7" fill="{FERRUGEM}" stroke="none" data-entra="cai" data-t="{0.8 + 0.08 * k:.2f}"/>' for k in range(5))
               + lupa + texto(640, 130, "roldana", 70, VERM, 'data-entra="pop" data-t="0.9"'), vb="120 80 860 640")


def cena3():
    """Enferruja, trava e o vidro racha."""
    rachaduras = (f'<path d="M500 420 l-60 70 l30 30 l-70 90 M500 420 l70 50 l-20 50 l80 70 M500 420 l10 -90 l-40 -40" fill="none" stroke="{TINTA}" stroke-width="5" '
                  f'data-entra="desenha" data-t="1.0" data-d="0.5" data-som="risco"/>')
    return svg(trilho_cima(250, 750, 160) + roldana(400, 220, 40, True) + roldana(600, 220, 40, True)
               + painel(330, 250, 340, 470, 'data-balanca="1.2" data-origem="50% 0%"') + rachaduras
               + texto(500, 110, "crec!", 80, VERM, 'data-entra="pop" data-t="1.2"'), vb="200 40 600 720")


def cena4():
    """A virada: ClaroFlex, sistema europeu."""
    brilhos = [(260, 300, 30, 0.4), (740, 280, 36, 0.5), (300, 620, 24, 0.6), (720, 640, 28, 0.7), (520, 250, 20, 0.8)]
    estrelas = "".join(f'<path d="M{x} {y - r} q{r * .25} {r * .75} {r} {r} q-{r * .75} {r * .25} -{r} {r} q-{r * .25} -{r * .75} -{r} -{r} q{r * .75} -{r * .25} {r} -{r}z" '
                       f'fill="{AMAR}" stroke-width="3" data-entra="pop" data-t="{t}" data-pulsa="0.1"/>' for x, y, r, t in brilhos)
    return svg(estrelas + texto(500, 470, "ClaroFlex", 120, TINTA, 'data-entra="zoom" data-t="0" data-d="0.5" data-som="impacto"')
               + texto(500, 560, "sistema europeu", 56, "#3f6fa8", 'data-entra="pop" data-t="0.6"', "Fredoka", 600), vb="200 170 600 540")


def cena5():
    """Sem roldanas: o vidro desliza no trilho inferior."""
    setas = "".join(f'<path d="M{430 + 120 * k} 520 v120 m-26 -26 l26 26 l26 -26" fill="none" stroke="{VERDE}" stroke-width="12" '
                    f'data-entra="desenha" data-t="{1.0 + 0.15 * k:.2f}" data-d="0.4"/>' for k in range(2))
    sem = (f'<g data-entra="pop" data-t="0.3"><circle cx="230" cy="170" r="56" fill="#ffffff"/><circle cx="230" cy="170" r="24" fill="#8f97a1"/>'
           f'<path d="M180 120 l100 100" stroke="{VERM}" stroke-width="14" fill="none"/></g>'
           + texto(250, 290, "sem roldana", 62, VERM, 'data-entra="pop" data-t="0.5"'))
    return svg(pista_baixo(100, 900, 720) + painel(560, 260, 200, 460, 'data-entra="dir" data-t="0" data-d="0.5" data-mover="-180,0"')
               + sem + setas + texto(520, 840, "desliza no trilho inferior", 62, VERDE, 'data-entra="pop" data-t="1.4"'), vb="120 90 820 780")


def cena6():
    """Visto de cima: os painéis deslizam pela frente da sacada e, na quina, viram e encostam na lateral, formando um L."""
    piso = (f'<rect x="200" y="250" width="620" height="400" fill="#fbf7f0" stroke="none"/>'
            f'<path d="M820 250 H200 V650" fill="none" stroke="#8f8577" stroke-width="16"/>'        # paredes (fundo e lateral)
            f'<rect x="200" y="652" width="620" height="16" rx="6" fill="{ALUM}"/>')               # pista na frente
    paineis = ""
    for k in range(5):
        x = 205 + 122 * k
        chega = 0.3 + 0.28 * k                      # cada painel desliza até a quina...
        dx = -(x - 205) + 30 * k                   # ...encosta um pouquinho ao lado do anterior...
        paineis += (f'<g data-mover="{dx},0" data-t="{chega:.2f}" data-mover-d="0.55" data-tomba="-90" data-tomba-t="{chega + 0.55:.2f}" '
                    f'data-origem="0% 50%"><rect x="{x}" y="645" width="116" height="22" rx="5" fill="{VIDRO}" fill-opacity=".9"/></g>')  # ...e vira 90°
    # o caminho em L: anda pela frente e sobe pela lateral
    seta = (f'<path d="M790 715 H262 V320" fill="none" stroke="{VERM}" stroke-width="12" stroke-dasharray="26 18" data-entra="desenha" data-t="0.15" data-d="1.6"/>'
            f'<path d="M238 350 l24 -30 l24 30" fill="none" stroke="{VERM}" stroke-width="12" data-entra="pop" data-t="1.7"/>')
    letra = texto(580, 470, "abre em L", 100, VERM, 'data-entra="pop" data-t="1.9" data-som="pop"')
    rotulos = (texto(520, 790, "desliza", 56, TINTA, 'data-entra="pop" data-t="0.5"', "Fredoka", 600)
               + texto(510, 220, "vista de cima", 44, "#8f8577", 'data-entra="fade" data-t="0.1"', "Fredoka", 600)
               + texto(580, 560, "sacada livre", 54, VERDE, 'data-entra="pop" data-t="2.3"', "Fredoka", 600))
    return svg(piso + paineis + seta + letra + rotulos, vb="140 170 760 670")


def cena8():
    """A sacada aberta: pôr do sol e a pessoa feliz."""
    sol = f'<circle cx="640" cy="330" r="90" fill="{AMAR}" data-entra="baixo" data-t="0.1" data-d="0.8" data-pulsa="0.03"/>'
    mar = f'<path d="M100 470 q100 -20 200 0 t200 0 t200 0 t200 0 V560 H100z" fill="#7fc3dc" stroke="none"/>'
    guarda = f'<rect x="100" y="560" width="800" height="20" rx="6" fill="{ALUM}"/>' + "".join(f'<path d="M{140 + 70 * k} 580 v170" stroke="{ALUM}" stroke-width="10" fill="none"/>' for k in range(12))
    vidros = "".join(painel(110 + 26 * k, 200, 30, 550) for k in range(3))
    return svg(f'<rect x="100" y="150" width="800" height="400" fill="{CEU}" stroke="none"/>' + sol + mar + guarda + vidros
               + pessoa(520, 870, 1.05, 'data-entra="pop" data-t="0.4"', "feliz", "alto")
               + texto(720, 130, "mais vista", 64, VERM, 'data-entra="pop" data-t="1.0"'), vb="90 80 820 790")


CENAS = [
    {"fala": "Sua cortina de vidro ainda *emperra* assim?", "visual": {"tipo": "ilustracao", "svg": cena1(), "onomatopeia": "ARGH!"}, "pausa": 0.35},
    {"fala": "O culpado mora lá em cima: a *roldana*.", "visual": {"tipo": "ilustracao", "svg": cena2(), "onomatopeia": "HMM?"}},
    {"fala": "Com o tempo, ela emperra, trava... e pode até *quebrar* o vidro.", "visual": {"tipo": "ilustracao", "svg": cena3(), "onomatopeia": "CREC!"}, "pausa": 0.35},
    {"fala": "Foi aí que a ClaroFlex, uma empresa *europeia*, desenvolveu um sistema que acaba com isso.", "visual": {"tipo": "marca", "logo": logo_claroflex(), "sub": "empresa europeia", "onomatopeia": "UAU!"}},
    {"fala": "Sem roldanas: o vidro desliza no *trilho inferior*.", "visual": {"tipo": "ilustracao", "svg": cena5(), "onomatopeia": "ZUUM!"}},
    {"fala": "E os painéis deslizam e abrem na lateral, em *L*, deixando a sacada livre.", "visual": {"tipo": "ilustracao", "svg": cena6(), "onomatopeia": "SHHH!"}},
    {"fala": "Adeus, roldana que *emperra*. Olá, vidro que desliza.", "visual": {"tipo": "riscado", "rotulo": "adeus", "antes": "roldana que emperra",
                                                                               "icone": "engrenagem", "depois": "vidro que desliza", "icone_depois": "check", "onomatopeia": "TCHAU!"}},
    {"fala": "Menos manutenção, mais *vista*.", "visual": {"tipo": "ilustracao", "svg": cena8(), "onomatopeia": "AAAH!"}},
    {"fala": "Quer na sua sacada? Faça seu *orçamento* no link da bio.", "visual": {"tipo": "marca", "logo": logo_claroflex(), "sub": "orçamento no link da bio", "onomatopeia": "BORA!"}},
]

roteiro = {"titulo": "ClaroFlex: cortina de vidro sem roldanas",
           "legenda_post": ("Sua cortina de vidro emperra ou trava? 😩 A ClaroFlex, empresa europeia, desenvolveu um sistema sem roldanas: "
                            "o vidro desliza no trilho inferior e abre na lateral em L. Menos manutenção, mais vista. 🌅 "
                            "Faça seu orçamento no link da bio! #claroflex #cortinadevidro #sacada #envidracamento #arquitetura #varanda"),
           "cenas": CENAS}
Path(__file__).with_name("roteiro.json").write_text(json.dumps(roteiro, ensure_ascii=False), encoding="utf-8")
print("ok", len(CENAS), "cenas")
