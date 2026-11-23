"""Roteiro de teste: 'Para que serve uma colhedeira de milho' - desenhos rústicos em SVG, animados pelo motor."""
import json
import random
from pathlib import Path

TINTA = "#3a2716"
MILHO = "#f0b73a"
FOLHA = "#6d8a3a"
FOLHA2 = "#4f6b2a"
VERM = "#b4402a"
PELE = "#e9b98a"
CEU = "#bcd6d8"
rnd = random.Random(4)

ESTILO = f'stroke="{TINTA}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"'


def svg(corpo: str, vb="0 0 1000 900") -> str:
    return f'<svg viewBox="{vb}" xmlns="http://www.w3.org/2000/svg"><g {ESTILO}>{corpo}</g></svg>'


def pe_milho(x, y, h=420, extra="", espiga=True, fase=0.0):
    """Um pé de milho com a base em (x, y)."""
    topo = y - h
    folhas = ""
    for k, (yy, lado) in enumerate([(0.25, -1), (0.42, 1), (0.6, -1), (0.75, 1)]):
        fy = y - h * yy
        dx = lado * (70 + 15 * k % 2)
        folhas += f'<path d="M{x} {fy} q{dx * 0.6} -{40} {dx} {30}" fill="none" stroke="{FOLHA2}"/>'
    esp = ""
    if espiga:
        ey = y - h * 0.5
        esp = (f'<path d="M{x + 4} {ey + 40} q30 -40 18 -110 q-30 30 -18 110z" fill="{FOLHA}"/>'
               f'<ellipse cx="{x + 24}" cy="{ey - 20}" rx="13" ry="40" fill="{MILHO}" transform="rotate(12 {x + 24} {ey - 20})"/>')
    pendao = "".join(f'<path d="M{x} {topo} l{d} -{35 + abs(d)}" fill="none"/>' for d in (-18, -6, 6, 18))
    return (f'<g data-balanca="1.6" data-fase="{fase:.2f}" data-origem="50% 100%" {extra}>'
            f'<path d="M{x} {y} Q{x - 8} {y - h / 2} {x} {topo}" fill="none" stroke="{FOLHA2}" stroke-width="9"/>'
            f'{folhas}{esp}{pendao}</g>')


def chapeu(cx, cy, s=1.0):
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{70 * s}" ry="{16 * s}" fill="#e8c46a"/>'
            f'<path d="M{cx - 38 * s} {cy - 4 * s} q{38 * s} -{70 * s} {76 * s} 0z" fill="#e8c46a"/>'
            f'<path d="M{cx - 36 * s} {cy - 12 * s} h{72 * s}" stroke="{VERM}" stroke-width="{7 * s}"/>')


def roceiro(cx, cy, s=1.0, cansado=False, extra=""):
    """Homem do campo (centro da cabeça em cx, cy)."""
    r = 42 * s
    olhos = (f'<path d="M{cx - 15 * s} {cy - 2 * s} l10 4 M{cx + 15 * s} {cy - 2 * s} l-10 4" fill="none"/>' if cansado else
             f'<circle cx="{cx - 14 * s}" cy="{cy - 2 * s}" r="4" fill="{TINTA}" stroke="none"/><circle cx="{cx + 14 * s}" cy="{cy - 2 * s}" r="4" fill="{TINTA}" stroke="none"/>')
    boca = (f'<path d="M{cx - 12 * s} {cy + 22 * s} q12 -8 24 0" fill="none"/>' if cansado else
            f'<path d="M{cx - 12 * s} {cy + 16 * s} q12 10 24 0" fill="none"/>')
    corpo_y = cy + r
    inclina = 'transform="rotate(14 %s %s)"' % (cx, corpo_y + 150 * s) if cansado else ""
    return (f'<g {extra}><g {inclina}>'
            f'<path d="M{cx - 60 * s} {corpo_y + 170 * s} q-6 -150 {60 * s} -160 q{66 * s} 10 {60 * s} 160z" fill="{VERM}"/>'
            f'<path d="M{cx - 30 * s} {corpo_y + 20 * s} v{150 * s} M{cx + 30 * s} {corpo_y + 20 * s} v{150 * s} M{cx - 60 * s} {corpo_y + 80 * s} h{120 * s}" stroke="#7a2a1c" stroke-width="4" fill="none"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{PELE}"/>{olhos}{boca}'
            f'<path d="M{cx - 18 * s} {cy + 8 * s} q18 14 36 0" fill="none" stroke="#a06a3a" stroke-width="4"/>'
            f'{chapeu(cx, cy - r * 0.7, s)}</g></g>')


def colhedeira(x, y, s=1.0, extra="", com_fumaca=True):
    """Colhedeira vista de lado, virada para a esquerda. (x, y) = chão embaixo da roda grande."""
    def P(px, py):
        return f"{x + px * s:.0f} {y + py * s:.0f}"
    fumaca = ""
    if com_fumaca:
        for k in range(3):
            fumaca += (f'<circle cx="{x + 140 * s:.0f}" cy="{y - 330 * s:.0f}" r="{18 + 8 * k}" fill="#d9cdb8" '
                       f'data-entra="fade" data-t="{0.4 + 0.35 * k:.2f}" data-d="0.4" data-mover="{30 + 20 * k},-{90 + 40 * k}"/>')
    return (f'<g {extra}>{fumaca}'
            # tanque de grãos e cano de descarga
            f'<path d="M{P(-40, -250)} L{P(150, -250)} L{P(130, -330)} L{P(-20, -330)}z" fill="{MILHO}"/>'
            f'<path d="M{P(140, -270)} L{P(170, -330)}" stroke-width="14"/>'
            # corpo
            f'<path d="M{P(-300, -60)} L{P(-300, -200)} L{P(-160, -200)} L{P(-160, -250)} L{P(180, -250)} L{P(220, -60)}z" fill="{VERM}"/>'
            # cabine
            f'<path d="M{P(-290, -200)} L{P(-280, -330)} L{P(-170, -330)} L{P(-160, -200)}z" fill="{CEU}"/>'
            f'<path d="M{P(-285, -335)} h{125 * s:.0f}" stroke-width="10"/>'
            f'<path d="M{P(-150, -150)} h{300 * s:.0f}" stroke="#7a2a1c" stroke-width="5"/>'
            # plataforma (frente) com as pontas que entram entre as fileiras
            f'<path d="M{P(-300, -40)} L{P(-470, -30)} L{P(-520, 0)} L{P(-300, 0)}z" fill="{MILHO}"/>'
            + "".join(f'<path d="M{P(-470 + 45 * k, -30)} l-{40 * s:.0f} 30" fill="none"/>' for k in range(4)) +
            # rodas
            f'<g data-girar="-200"><circle cx="{x + 60 * s:.0f}" cy="{y - 80 * s:.0f}" r="{80 * s:.0f}" fill="#2b241e"/>'
            f'<circle cx="{x + 60 * s:.0f}" cy="{y - 80 * s:.0f}" r="{30 * s:.0f}" fill="{MILHO}"/>'
            f'<path d="M{x + 60 * s:.0f} {y - 150 * s:.0f} v{140 * s:.0f}" stroke="{MILHO}" stroke-width="6"/></g>'
            f'<g data-girar="-320"><circle cx="{x - 200 * s:.0f}" cy="{y - 45 * s:.0f}" r="{45 * s:.0f}" fill="#2b241e"/>'
            f'<circle cx="{x - 200 * s:.0f}" cy="{y - 45 * s:.0f}" r="{16 * s:.0f}" fill="{MILHO}"/>'
            f'<path d="M{x - 200 * s:.0f} {y - 85 * s:.0f} v{80 * s:.0f}" stroke="{MILHO}" stroke-width="5"/></g>'
            '</g>')


def sol(cx, cy, r=60, extra='data-entra="zoom" data-t="0.1"'):
    raios = "".join(f'<path d="M{cx + (r + 18) * c:.0f} {cy + (r + 18) * s_:.0f} l{22 * c:.0f} {22 * s_:.0f}" fill="none"/>'
                    for c, s_ in [(1, 0), (-1, 0), (0, 1), (0, -1), (.7, .7), (-.7, .7), (.7, -.7), (-.7, -.7)])
    return f'<g {extra} data-pulsa="0.03"><circle cx="{cx}" cy="{cy}" r="{r}" fill="#f6d27a"/>{raios}</g>'


def chao(y=820):
    return f'<path d="M0 {y} q250 -18 500 0 t500 0" fill="none" stroke-width="7"/>'


# ---------------------------------------------------------------- cenas
def cena1():
    """Milharal enorme e um roceiro pequenininho com um cestinho."""
    pes = ""
    k = 0
    for linha, (yb, h) in enumerate([(640, 380), (720, 440), (800, 500)]):
        for i in range(6):
            x = 90 + i * 165 + (40 if linha % 2 else 0) + rnd.randint(-15, 15)
            if linha == 2 and 360 < x < 640:
                continue  # espaço para o roceiro
            pes += pe_milho(x, yb, h, extra=f'data-entra="baixo" data-t="{0.05 + 0.05 * k:.2f}" data-d="0.5"', fase=rnd.random() * 6)
            k += 1
    gota = (f'<path d="M560 520 q-10 18 0 26 q10 -8 0 -26z" fill="#8cc4e0" data-entra="cai" data-t="1.4" data-d="0.6"/>')
    cesto = f'<path d="M440 760 h110 l-12 60 h-86z" fill="#c98f4a"/><path d="M450 775 h90 M455 792 h80" fill="none" stroke-width="4"/>'
    return svg(sol(860, 150) + pes + chao(820) + "",
               vb="0 70 1000 790") if False else svg(sol(860, 150) + pes + chao(820) +
               f'<g data-entra="pop" data-t="0.9" data-d="0.6">{roceiro(500, 600, 0.75)}{cesto}</g>' + gota, vb="20 80 960 770")


def cena2():
    """Calendário enchendo de X e o roceiro com a mão nas costas."""
    cal = (f'<rect x="80" y="140" width="520" height="560" rx="14" fill="#fff4dc"/>'
           f'<rect x="80" y="140" width="520" height="110" rx="14" fill="{VERM}"/>'
           f'<path d="M180 120 v50 M500 120 v50" stroke-width="12"/>'
           f'<text x="340" y="215" text-anchor="middle" font-family="Caveat" font-size="64" fill="#fff4dc" stroke="none">colheita</text>')
    xs = ""
    for i in range(20):
        c, l = i % 5, i // 5
        cx, cy = 130 + c * 100, 300 + l * 100
        cal += f'<text x="{cx}" y="{cy + 12}" text-anchor="middle" font-family="Inter" font-size="30" fill="{TINTA}" stroke="none" opacity=".5">{i + 1}</text>'
        xs += (f'<path d="M{cx - 30} {cy - 28} l60 60 M{cx + 30} {cy - 28} l-60 60" stroke="{VERM}" stroke-width="7" fill="none" '
               f'data-entra="desenha" data-t="{0.2 + i * 0.08:.2f}" data-d="0.25"/>')
    ai = (f'<g data-entra="pop" data-t="1.3"><path d="M760 230 q80 -10 90 50 q-10 50 -80 45 l-30 30 l5 -35 q-50 -20 15 -90z" fill="#fff4dc"/>'
          f'<text x="800" y="300" text-anchor="middle" font-family="Caveat" font-size="70" fill="{VERM}" stroke="none">ai!</text></g>')
    return svg(f'<g data-entra="esq" data-t="0" data-d="0.45">{cal}</g>' + xs +
               f'<g data-entra="dir" data-t="0.25" data-d="0.5">{roceiro(800, 470, 0.95, cansado=True)}'
               f'<path d="M760 640 q-40 30 -10 70" fill="none" stroke-width="10"/></g>' + ai + chao(860), vb="40 100 940 780")


def cena3():
    """A colhedeira chega na plantação, fazendo fumaça."""
    pes = "".join(pe_milho(80 + i * 120, 820, 330, fase=i) for i in range(3))
    return svg(sol(170, 330, 45) + pes + chao(820) +
               colhedeira(700, 820, 1.0, extra='data-entra="dir" data-t="0" data-d="1.1" data-mover="-120,0" data-som="motor" data-som-d="2.6"'), vb="20 250 960 600")


def cena4():
    """Close na plataforma: as pontas passam entre os pés e eles vão caindo."""
    pes = ""
    xs = [190, 330, 470, 610]
    for i, x in enumerate(xs):
        t = 0.55 + (len(xs) - 1 - i) * 0.38  # caem da direita para a esquerda, conforme a plataforma passa
        pes += pe_milho(x, 800, 480, fase=i).replace("<g data-balanca", f'<g data-tomba="-82" data-tomba-t="{t:.2f}" data-balanca', 1)
    plataforma = (f'<g data-entra="dir" data-t="0" data-d="0.4" data-mover="-620,0">'
                  f'<path d="M760 610 L1300 600 L1300 820 L700 820z" fill="{MILHO}"/>'
                  + "".join(f'<path d="M{760 + 120 * k} {610 - 2 * k} l-90 140 l90 70z" fill="{VERM}"/>' for k in range(5)) +
                  f'<path d="M780 690 h500" stroke="#7a2a1c" stroke-width="5" fill="none"/>'
                  f'<g data-girar="-360"><circle cx="1180" cy="700" r="50" fill="#2b241e"/><path d="M1130 700 h100 M1180 650 v100" stroke="{MILHO}" stroke-width="7"/></g></g>')
    setas = "".join(f'<path d="M{300 + 160 * k} 560 q60 -30 120 0 l-20 -18 m20 18 l-24 10" fill="none" stroke="{VERM}" stroke-width="6" '
                    f'data-entra="desenha" data-t="{1.2 + 0.2 * k:.2f}" data-d="0.4"/>' for k in range(2))
    return svg(pes + plataforma + setas + chao(820), vb="40 240 940 600")


def cena5():
    """Corte de dentro da máquina: entra a espiga, sai grão de um lado, sabugo e palha do outro."""
    caixa = (f'<g data-entra="desenha" data-t="0" data-d="0.7">'
             f'<rect x="300" y="250" width="400" height="330" rx="24" fill="#d8c29a"/>'
             f'<circle cx="420" cy="420" r="70" fill="#c4a774"/><circle cx="580" cy="420" r="55" fill="#c4a774"/></g>')
    engrenagem = (f'<g data-girar="140"><circle cx="420" cy="420" r="40" fill="{MILHO}"/>'
                  + "".join(f'<path d="M420 420 l{52 * c:.0f} {52 * s_:.0f}" stroke-width="10" fill="none"/>' for c, s_ in [(1, 0), (0, 1), (-1, 0), (0, -1)]) + '</g>'
                  f'<g data-girar="-180"><circle cx="580" cy="420" r="30" fill="{MILHO}"/>'
                  + "".join(f'<path d="M580 420 l{40 * c:.0f} {40 * s_:.0f}" stroke-width="9" fill="none"/>' for c, s_ in [(.7, .7), (-.7, .7), (.7, -.7), (-.7, -.7)]) + '</g>')
    espiga = (f'<g data-entra="esq" data-t="0.4" data-d="0.6"><path d="M80 420 q80 -50 190 0 q-110 50 -190 0z" fill="{MILHO}"/>'
              f'<path d="M80 420 q-20 -40 -50 -50 M80 420 q-20 40 -50 50" fill="none" stroke="{FOLHA2}" stroke-width="8"/></g>')
    graos = "".join(f'<ellipse cx="{560 + rnd.randint(0, 140)}" cy="{700 + rnd.randint(0, 110)}" rx="15" ry="19" fill="{MILHO}" '
                    f'data-entra="cai" data-t="{1.1 + 0.05 * i:.2f}" data-d="0.5"/>' for i in range(16))
    sabugo = (f'<g data-entra="dir" data-t="1.5" data-d="0.6"><rect x="760" y="300" width="170" height="44" rx="22" fill="#d8a86a"/>'
              + "".join(f'<path d="M{790 + 25 * k} 230 q20 -40 50 -20" fill="none" stroke="{FOLHA}" stroke-width="7"/>' for k in range(4)) + '</g>')
    rotulos = (f'<text x="640" y="880" text-anchor="middle" font-family="Caveat" font-size="62" fill="{VERM}" stroke="none" data-entra="pop" data-t="1.6">grão!</text>'
               f'<text x="845" y="410" text-anchor="middle" font-family="Caveat" font-size="48" fill="{TINTA}" stroke="none" data-entra="pop" data-t="1.9">sabugo e palha</text>'
               f'<path d="M640 590 v80 m-22 -22 l22 22 l22 -22" fill="none" stroke="{VERM}" stroke-width="7" data-entra="desenha" data-t="1.0" data-d="0.3"/>'
               f'<path d="M705 330 h50 m-20 -20 l20 20 l-20 20" fill="none" stroke="{VERM}" stroke-width="7" data-entra="desenha" data-t="1.4" data-d="0.3"/>')
    som = '<g data-som="graos" data-som-d="1.2" data-t="1.1"></g>'
    return svg(caixa + engrenagem + espiga + graos + sabugo + rotulos + som, vb="20 200 950 710")


def cena6():
    """A colhedeira despeja o grão no caminhão."""
    caminhao = (f'<g data-entra="esq" data-t="0.1" data-d="0.8">'
                f'<path d="M40 560 h330 v160 h-330z" fill="#8a6a44"/>'
                f'<path d="M370 610 h110 l40 60 v50 h-150z" fill="{CEU}"/>'
                f'<g data-girar="-260"><circle cx="110" cy="740" r="42" fill="#2b241e"/><circle cx="110" cy="740" r="14" fill="{MILHO}"/></g>'
                f'<g data-girar="-260"><circle cx="430" cy="740" r="42" fill="#2b241e"/><circle cx="430" cy="740" r="14" fill="{MILHO}"/></g>'
                f'<path d="M60 560 q140 -60 290 0z" fill="{MILHO}" data-entra="zoom" data-t="1.8" data-d="0.8" data-origem="50% 100%"/></g>')
    maquina = colhedeira(820, 790, 0.82, com_fumaca=False)
    cano = (f'<path d="M790 470 L660 400 L380 400 L370 430" fill="none" stroke="{TINTA}" stroke-width="26" data-entra="desenha" data-t="0.5" data-d="0.5"/>'
            f'<path d="M790 470 L660 400 L380 400 L370 430" fill="none" stroke="{MILHO}" stroke-width="12" data-entra="desenha" data-t="0.55" data-d="0.5"/>')
    graos = "".join(f'<ellipse cx="{340 + rnd.randint(0, 60)}" cy="{470 + rnd.randint(0, 60)}" rx="11" ry="14" fill="{MILHO}" '
                    f'data-entra="cai" data-t="{1.0 + 0.07 * i:.2f}" data-d="0.45"/>' for i in range(18))
    return svg(chao(790) + caminhao + maquina + cano + graos.replace('data-t="1.00"', 'data-t="1.00" data-som="graos" data-som-d="1.6"', 1), vb="20 330 970 500")


CENAS = [
    {"fala": "Imagina colher um *milharal* inteiro... na mão.", "visual": {"tipo": "ilustracao", "svg": cena1()}},
    {"fala": "Levaria *semanas*, e haja costas!", "visual": {"tipo": "ilustracao", "svg": cena2()}},
    {"fala": "É aí que entra a *colhedeira*.", "visual": {"tipo": "ilustracao", "svg": cena3()}},
    {"fala": "Na frente, a plataforma *corta* e puxa os pés de milho.", "visual": {"tipo": "ilustracao", "svg": cena4()}},
    {"fala": "Lá dentro, ela separa o *grão* do sabugo e da palha.", "visual": {"tipo": "ilustracao", "svg": cena5()}},
    {"fala": "O grão vai pro *tanque*, e depois direto pro caminhão.", "visual": {"tipo": "ilustracao", "svg": cena6()}},
    {"fala": "O que levava semanas... agora leva *um dia*.", "visual": {"tipo": "riscado", "rotulo": "antes", "antes": "semanas de colheita", "icone": "relogio", "depois": "um dia", "icone_depois": "check"}},
    {"fala": "Quer ver ela trabalhando de verdade? Comenta *MILHO*.", "visual": {"tipo": "cta", "palavra": "MILHO", "rotulo": "COMENTA"}},
]

roteiro = {"titulo": "Para que serve uma colhedeira de milho",
           "legenda_post": "Pra que serve uma colhedeira de milho? 🌽🚜 Em 30 segundos você entende. #agro #milho #colheita #agronegocio #campo",
           "cenas": CENAS}
Path(__file__).with_name("roteiro.json").write_text(json.dumps(roteiro, ensure_ascii=False), encoding="utf-8")
print("ok", len(CENAS), "cenas")
