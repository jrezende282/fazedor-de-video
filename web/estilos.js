/* 16 estilos de animação ("acabamentos"). O mesmo desenho do roteiro vira cartoon chapado, pixel art,
   rabisco de caderno, recorte de papel, lousa, neon anos 80, minimalista com contador, teatro de sombras,
   massinha, xilogravura de cordel, planta técnica, low poly, filme mudo, quadrinhos, terminal ou 3D.
   Cada estilo define: fundo, filtro aplicado ao desenho, se o desenho "se desenha" sozinho, ritmo dos quadros
   (stop motion) e enfeites que mudam com o tempo. As cores e fontes ficam em estilos.css. */
"use strict";

function _rnd(semente) { let s = semente >>> 0 || 1; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }

const _FILTROS = `
<filter id="f-pixel" color-interpolation-filters="sRGB" x="0" y="0" width="1" height="1">
  <feFlood x="5" y="5" width="3" height="3"/><feComposite width="13" height="13"/><feTile result="a"/>
  <feComposite in="SourceGraphic" in2="a" operator="in"/><feMorphology operator="dilate" radius="6.5"/></filter>
<filter id="f-papel" color-interpolation-filters="sRGB" x="-10%" y="-10%" width="120%" height="120%">
  <feDropShadow dx="5" dy="8" stdDeviation="3" flood-color="#3b2a14" flood-opacity=".38"/></filter>
<filter id="f-massinha" color-interpolation-filters="sRGB" x="-10%" y="-10%" width="120%" height="120%">
  <feTurbulence id="massinha-ruido" type="fractalNoise" baseFrequency="0.013" numOctaves="2" seed="2" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="10" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feGaussianBlur in="d" stdDeviation="5" result="b"/>
  <feSpecularLighting in="b" surfaceScale="6" specularConstant=".75" specularExponent="16" lighting-color="#ffffff" result="s">
    <feDistantLight azimuth="235" elevation="48"/></feSpecularLighting>
  <feComposite in="s" in2="d" operator="in" result="s2"/>
  <feComposite in="d" in2="s2" operator="arithmetic" k1="0" k2="1" k3=".55" k4="0" result="m"/>
  <feDropShadow in="m" dx="4" dy="10" stdDeviation="6" flood-color="#3a2a40" flood-opacity=".35"/></filter>
<filter id="f-3d" color-interpolation-filters="sRGB" x="-10%" y="-10%" width="120%" height="125%">
  <feGaussianBlur in="SourceAlpha" stdDeviation="7" result="b"/>
  <feSpecularLighting in="b" surfaceScale="7" specularConstant=".9" specularExponent="22" lighting-color="#ffffff" result="s">
    <fePointLight x="-300" y="-500" z="700"/></feSpecularLighting>
  <feComposite in="s" in2="SourceAlpha" operator="in" result="s2"/>
  <feDiffuseLighting in="b" surfaceScale="5" diffuseConstant="1" lighting-color="#ffffff" result="d">
    <feDistantLight azimuth="235" elevation="55"/></feDiffuseLighting>
  <feComposite in="d" in2="SourceAlpha" operator="in" result="d2"/>
  <feBlend in="SourceGraphic" in2="d2" mode="multiply" result="som"/>
  <feComposite in="som" in2="s2" operator="arithmetic" k1="0" k2="1" k3=".6" k4="0" result="luz"/>
  <feDropShadow in="luz" dx="0" dy="18" stdDeviation="12" flood-color="#1d2a44" flood-opacity=".3"/></filter>
<filter id="f-lowpoly" color-interpolation-filters="sRGB" x="-5%" y="-5%" width="110%" height="110%">
  <feTurbulence type="fractalNoise" baseFrequency="0.006" numOctaves="1" seed="9" result="n"/>
  <feComponentTransfer in="n" result="q"><feFuncR type="discrete" tableValues=".75 .9 1 1.1"/><feFuncG type="discrete" tableValues=".75 .9 1 1.1"/>
    <feFuncB type="discrete" tableValues=".75 .9 1 1.1"/></feComponentTransfer>
  <feBlend in="SourceGraphic" in2="q" mode="multiply" result="f"/>
  <feComposite in="f" in2="SourceAlpha" operator="in"/></filter>
<filter id="f-xilo" color-interpolation-filters="sRGB" x="-5%" y="-5%" width="110%" height="110%">
  <feColorMatrix type="saturate" values="0" result="c"/>
  <feTurbulence type="fractalNoise" baseFrequency=".9 .02" numOctaves="1" seed="3" result="veio"/>
  <feColorMatrix in="veio" type="matrix" values="0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 1" result="v2"/>
  <feBlend in="c" in2="v2" mode="multiply" result="cv"/>
  <feComponentTransfer in="cv"><feFuncR type="discrete" tableValues=".11 .11 .94 .94 .94"/><feFuncG type="discrete" tableValues=".08 .08 .9 .9 .9"/>
    <feFuncB type="discrete" tableValues=".06 .06 .8 .8 .8"/></feComponentTransfer>
  <feComposite in2="SourceAlpha" operator="in"/></filter>
<filter id="f-sombra" color-interpolation-filters="sRGB" x="-5%" y="-5%" width="110%" height="110%">
  <feColorMatrix type="matrix" values="0 0 0 0 .1  0 0 0 0 .06  0 0 0 0 .04  0 0 0 1 0"/><feGaussianBlur stdDeviation=".8"/></filter>
<filter id="f-branco" color-interpolation-filters="sRGB" x="-5%" y="-5%" width="110%" height="110%">
  <feColorMatrix type="matrix" values="0 0 0 0 .96  0 0 0 0 .96  0 0 0 0 .96  0 0 0 1 0"/></filter>
<filter id="f-neon" color-interpolation-filters="sRGB" x="-15%" y="-15%" width="130%" height="130%">
  <feGaussianBlur stdDeviation="5" result="b"/><feGaussianBlur in="SourceGraphic" stdDeviation="14" result="b2"/>
  <feMerge><feMergeNode in="b2"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="f-terminal" color-interpolation-filters="sRGB" x="-10%" y="-10%" width="120%" height="120%">
  <feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>`;

function _ceuEstrelas(n, semente, cor) {
  const r = _rnd(semente);
  return Array.from({ length: n }, () => `<rect x="${(r() * 100).toFixed(1)}%" y="${(r() * 55).toFixed(1)}%" width="${r() < .2 ? 9 : 6}" height="${r() < .2 ? 9 : 6}" fill="${cor}"/>`).join("");
}

function _lowpoly(W, H) {
  const r = _rnd(5), col = 7, lin = 13, pts = [];
  for (let j = 0; j <= lin; j++) for (let i = 0; i <= col; i++)
    pts.push([i * W / col + (i && i < col ? (r() - .5) * W / col * .7 : 0), j * H / lin + (j && j < lin ? (r() - .5) * H / lin * .7 : 0)]);
  const P = (i, j) => pts[j * (col + 1) + i];
  let s = "";
  for (let j = 0; j < lin; j++) for (let i = 0; i < col; i++) {
    const a = P(i, j), b = P(i + 1, j), c = P(i, j + 1), d = P(i + 1, j + 1);
    const chao = j > lin * .72;
    for (const tri of [[a, b, c], [b, d, c]]) {
      const y = (tri[0][1] + tri[1][1] + tri[2][1]) / 3 / H;
      const l = chao ? 34 + r() * 14 : 48 + y * 30 + r() * 10;
      const cor = chao ? `hsl(${120 + r() * 20} 38% ${l}%)` : `hsl(${205 + r() * 12} 62% ${l}%)`;
      s += `<polygon points="${tri.map(p => p.map(v => v.toFixed(0)).join(",")).join(" ")}" fill="${cor}" stroke="${cor}" stroke-width="1"/>`;
    }
  }
  return `<svg class="cheio" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">${s}</svg>`;
}

const ONOMATOPEIAS = ["VRUUM!", "POW!", "BOOM!", "ZAP!", "UAU!", "PLIM!", "CRASH!", "WOW!"];

window.ACABAMENTOS = {
  chapado: {
    nome: "Cartoon chapado",
    fundo: () => `<div class="ceu"></div><svg class="cheio" viewBox="0 0 100 100" preserveAspectRatio="none">
      <path d="M0 86 Q30 79 55 84 T100 82 V100 H0z" fill="#20283a"/></svg><div class="sol"></div>`,
  },
  pixel: {
    nome: "Pixel art", filtro: "url(#f-pixel)", quadros: 10,
    fundo: () => `<div class="ceu"></div><svg class="cheio">${_ceuEstrelas(60, 3, "#fff6c8")}</svg><div class="lua"></div><div class="grama"></div>`,
  },
  caderno: {
    nome: "Rabisco de caderno", rabisco: 5, desenharTudo: true, quadros: 12,
    fundo: () => `<div class="pautas"></div><div class="margem"></div><div class="furos"><i></i><i></i><i></i></div>`,
  },
  recorte: {
    nome: "Recorte de papel", filtro: "url(#f-papel)", quadros: 12,
    fundo: () => `<div class="ceu"></div><div class="textura"></div>
      <svg class="cheio" viewBox="0 0 100 100" preserveAspectRatio="none" style="filter:url(#f-papel)">
      <path d="M0 80 Q25 70 50 78 T100 74 V100 H0z" fill="#8fb36b"/><path d="M0 88 Q35 80 65 88 T100 86 V100 H0z" fill="#6f9a4e"/></svg>
      <div class="sol"></div>`,
  },
  lousa: {
    nome: "Lousa branca", rabisco: 2, desenharTudo: true,
    fundo: () => `<div class="quadro"></div><div class="reflexo-lousa"></div>`,
    moldura: () => `<div class="caneta-lousa"></div>`,
  },
  neon80: {
    nome: "Neon anos 80", filtro: "url(#f-neon)",
    fundo: () => `<div class="ceu"></div><div class="sol-80"></div><div class="chao-80"><div class="grade-80"></div></div>`,
    atualizar: (t, c, ctx) => { const g = ctx.fundo.querySelector(".grade-80"); if (g) g.style.backgroundPosition = `0 ${(t * 120) % 120}px`; },
  },
  minimal: {
    nome: "Minimalista com contador", filtro: "url(#f-branco)",
    fundo: () => ``,
    moldura: () => `<div class="contador"><b>0</b><span>visualizações</span></div>`,
    atualizar: (t, c, ctx) => {
      const b = ctx.moldura.querySelector(".contador b"); if (!b) return;
      const total = (window.DADOS.molde.contador_final || 140435), x = Math.min(1, t / Math.max(1, window.DADOS.duracao - 1));
      b.textContent = Math.round(total * (1 - Math.pow(1 - x, 2.2))).toLocaleString("pt-BR");
    },
  },
  sombras: {
    nome: "Teatro de sombras", filtro: "url(#f-sombra)",
    fundo: () => `<div class="ceu"></div><div class="sol"></div><svg class="cheio" viewBox="0 0 100 100" preserveAspectRatio="none">
      <path d="M0 84 Q20 78 40 83 Q62 88 80 81 T100 82 V100 H0z" fill="#1a0f08"/></svg><div class="vinheta-s"></div>`,
  },
  massinha: {
    nome: "Massinha (stop motion)", filtro: "url(#f-massinha)", quadros: 12,
    fundo: () => `<div class="ceu"></div><div class="textura"></div><svg class="cheio" viewBox="0 0 100 100" preserveAspectRatio="none" style="filter:url(#f-massinha)">
      <path d="M-5 84 Q25 78 50 84 T105 82 V105 H-5z" fill="#7cc46a"/></svg>`,
    atualizar: (t) => { const n = document.getElementById("massinha-ruido"); if (n) n.setAttribute("seed", String(1 + Math.floor(t * 12) % 3)); },
  },
  cordel: {
    nome: "Xilogravura de cordel", filtro: "url(#f-xilo)", rabisco: 3, quadros: 12,
    fundo: () => `<div class="papel-x"></div><svg class="cheio" viewBox="0 0 100 100" preserveAspectRatio="none">
      ${Array.from({ length: 16 }, (_, i) => `<path d="M${82 + 9 * Math.cos(i / 16 * 6.28)} ${11 + 5 * Math.sin(i / 16 * 6.28)} L${82 + 14 * Math.cos(i / 16 * 6.28)} ${11 + 8 * Math.sin(i / 16 * 6.28)}" stroke="#1c140e" stroke-width=".6"/>`).join("")}
      <ellipse cx="82" cy="11" rx="5" ry="2.9" fill="none" stroke="#1c140e" stroke-width=".8"/>
      ${Array.from({ length: 9 }, (_, i) => `<path d="M0 ${86 + i * 1.6} Q50 ${82 + i * 1.6} 100 ${86 + i * 1.6}" stroke="#1c140e" stroke-width=".55" fill="none"/>`).join("")}</svg>
      <div class="borda-x"></div>`,
  },
  planta: {
    nome: "Planta técnica", desenharTudo: true,
    fundo: () => `<div class="azul"></div><div class="grade-p"></div><div class="grade-p fina"></div>`,
    moldura: () => `<div class="cota">ALTITUDE: <b>0</b> m<br>CENA: <i>01</i></div><div class="carimbo-p">PROJETO · ESC 1:1<br>FOLHA <i>01</i></div>`,
    atualizar: (t, c, ctx) => {
      const b = ctx.moldura.querySelector(".cota b"); if (b) b.textContent = Math.round(t * 173.4).toLocaleString("pt-BR");
      ctx.moldura.querySelectorAll("i").forEach(i => i.textContent = String(c ? c.n : 1).padStart(2, "0"));
    },
  },
  lowpoly: {
    nome: "Low poly 3D", filtro: "url(#f-lowpoly)",
    fundo: (W, H) => _lowpoly(W, H),
  },
  filme: {
    nome: "Filme mudo", quadros: 16,
    fundo: () => `<div class="tela-cinza"></div>`,
    moldura: () => `<div class="grao"></div><div class="riscos"><i></i><i></i></div><div class="vinheta-f"></div>`,
    atualizar: (t, c, ctx) => {
      const q = Math.floor(t * 16), r = _rnd(q + 7);
      const g = ctx.moldura.querySelector(".grao"); if (g) g.style.backgroundPosition = `${(r() * 300) | 0}px ${(r() * 300) | 0}px`;
      ctx.moldura.querySelectorAll(".riscos i").forEach((i, k) => { i.style.left = `${(r() * 100).toFixed(1)}%`; i.style.opacity = r() < .55 ? .5 : 0; });
      document.querySelector(".camera").style.filter = `grayscale(1) sepia(.18) contrast(1.25) brightness(${(0.9 + r() * 0.16).toFixed(2)})`;
    },
  },
  quadrinhos: {
    nome: "História em quadrinhos",
    fundo: () => `<div class="ceu"></div><div class="reticula"></div>`,
    moldura: () => `<div class="painel-hq"></div><div class="balao-hq"><span></span></div>`,
    atualizar: (t, c, ctx) => {
      const b = ctx.moldura.querySelector(".balao-hq"); if (!b || !c) return;
      const d = t - c.ini, x = Math.min(1, d / 0.35);
      b.querySelector("span").textContent = (c.visual && c.visual.onomatopeia) || ONOMATOPEIAS[(c.n - 1) % ONOMATOPEIAS.length];
      const mola = x >= 1 ? 1 : 1 - Math.exp(-6 * x) * Math.cos(9 * x);
      b.style.transform = `rotate(-12deg) scale(${d < 1.3 ? mola : Math.max(0, 1 - (d - 1.3) * 4)})`;
    },
  },
  terminal: {
    nome: "Terminal de código", filtro: "url(#f-terminal)", quadros: 15,
    fundo: () => `<div class="crt"></div>`,
    moldura: () => `<div class="prompt">$ animatik --render<br>&gt; cena <i>01</i> · <b>0</b> quadros</div><div class="linhas-crt"></div>`,
    atualizar: (t, c, ctx) => {
      const b = ctx.moldura.querySelector(".prompt b"); if (b) b.textContent = Math.floor(t * 30);
      const i = ctx.moldura.querySelector(".prompt i"); if (i) i.textContent = String(c ? c.n : 1).padStart(2, "0");
    },
  },
  real3d: {
    nome: "3D de verdade", filtro: "url(#f-3d)",
    fundo: () => `<div class="ceu"></div><div class="piso"></div>`,
  },
};

window.instalarAcabamento = function (nome) {
  const A = window.ACABAMENTOS[nome] || window.ACABAMENTOS.chapado;
  const defs = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  defs.setAttribute("width", "0"); defs.setAttribute("height", "0"); defs.style.position = "absolute";
  defs.innerHTML = _FILTROS;
  document.body.appendChild(defs);
  document.body.classList.add("acab-" + (window.ACABAMENTOS[nome] ? nome : "chapado"));
  return A;
};
