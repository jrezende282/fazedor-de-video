/* Motor de animação do Animatik.
   Tudo é desenhado em função do tempo t (segundos): desenhar(t) deixa a tela exatamente como ela é naquele
   instante. Assim o vídeo sai igual sempre (o gravador tira uma foto por quadro). Nada de animação do CSS. */
"use strict";

// ------------------------------------------------------------------ utilidades
const lim = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const prog = (t, ini, dur) => lim((t - ini) / Math.max(dur, 1e-6));
const suave = x => x * x * (3 - 2 * x);
const saida = x => 1 - Math.pow(1 - x, 3);           // easeOutCubic
const saidaForte = x => 1 - Math.pow(1 - x, 5);      // easeOutQuint
const mola = x => { if (x <= 0) return 0; if (x >= 1) return 1; return 1 - Math.exp(-6 * x) * Math.cos(9 * x); };
const misturar = (a, b, x) => a + (b - a) * x;
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
function aleatorio(semente) { let s = semente >>> 0 || 1; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }
function el(tag, classe, html) { const e = document.createElement(tag); if (classe) e.className = classe; if (html != null) e.innerHTML = html; return e; }
const pad = (n, k = 2) => String(n).padStart(k, "0");
const relogio = s => `${pad(Math.floor(s / 3600))}:${pad(Math.floor(s / 60) % 60)}:${pad(Math.floor(s) % 60)}`;

const D = window.DADOS;
const M = D.molde;
const palco = document.getElementById("palco");
const raiz = document.documentElement;

// ------------------------------------------------------------------ tema (cores e fontes do molde)
function aplicarTema() {
  document.body.classList.add("tema-" + M.base, "formato-" + (M.formato || "vertical"));
  const c = M.cores || {}, f = M.fontes || {};
  const vars = {
    "--fundo": c.fundo, "--fundo2": c.fundo2, "--texto": c.texto, "--suave": c.suave,
    "--destaque": c.destaque, "--destaque2": c.destaque2, "--linha": c.linha,
    "--f-titulo": f.titulo, "--f-texto": f.texto, "--f-mono": f.mono, "--f-destaque": f.destaque, "--f-mao": f.mao,
  };
  // cores que o molde não define saem das outras (assim um molde novo fica coerente com qualquer cor)
  if (!c.linha && c.destaque) vars["--linha"] = `color-mix(in srgb, ${c.destaque} 30%, transparent)`;
  if (!c.suave && c.texto) vars["--suave"] = `color-mix(in srgb, ${c.texto} 55%, transparent)`;
  if (!c.fundo2 && c.fundo && c.destaque) vars["--fundo2"] = `color-mix(in srgb, ${c.fundo} 88%, ${c.destaque})`;
  for (const [k, v] of Object.entries(vars)) if (v) raiz.style.setProperty(k, v);
  // o palco: vertical = tela inteira; monitor = 16:9 dentro de um monitor filmado na mesa
  const [W, H] = M.formato === "monitor" ? [1600, 900] : [D.largura, D.altura];
  raiz.style.setProperty("--W", W + "px");
  raiz.style.setProperty("--H", H + "px");
  raiz.style.setProperty("--u", (M.formato === "monitor" ? H / 100 : Math.min(W, H * 0.62) / 100) + "px");  // unidade de tamanho
  return [W, H];
}
const [PW, PH] = aplicarTema();

// ------------------------------------------------------------------ camadas fixas
const cena3d = el("div", "camera");        // "câmera": leve aproximação e tremida
palco.appendChild(cena3d);
const fundo = el("div", "fundo");
cena3d.appendChild(fundo);
const moldura = el("div", "moldura");      // cantos, rótulos, REC...
cena3d.appendChild(moldura);
const camadaCenas = el("div", "cenas");
cena3d.appendChild(camadaCenas);
const flash = el("div", "flash");
cena3d.appendChild(flash);

let atualizarMoldura = () => {};
let ACAB = null;  // acabamento (só na base "estilo")
if (M.base === "neon") {
  fundo.innerHTML = `<div class="grade"></div><div class="chao"></div><div class="poeira"></div><div class="vinheta"></div><div class="varredura"></div>`;
  const rnd = aleatorio(7), poeira = fundo.querySelector(".poeira");
  const pontos = [];
  for (let i = 0; i < 46; i++) {
    const p = el("i"); poeira.appendChild(p);
    pontos.push({ p, x: rnd() * 100, y: rnd() * 100, v: 0.6 + rnd() * 2, f: rnd() * 6, s: 1 + rnd() * 2.5 });
  }
  moldura.innerHTML = `
    <b class="canto c1">+</b><b class="canto c2">+</b><b class="canto c3">+</b><b class="canto c4">+</b>
    <div class="rot r-sup-esq"><span class="marca">${esc(M.marca || "ANIMATIK")}</span> / <span class="num">001</span></div>
    <div class="rot r-sup-dir"><i class="rec"></i>REC <span class="tempo">00:00:00</span></div>
    <div class="rot r-inf-esq"><span class="tipo">CENA</span></div>
    <div class="rot r-inf-dir"><span class="cont">${pad(D.cenas.length)} CENAS</span></div>`;
  const num = moldura.querySelector(".num"), tempo = moldura.querySelector(".tempo");
  const tipo = moldura.querySelector(".tipo"), rec = moldura.querySelector(".rec");
  const inicioRec = 600 + (M.semente || 3) * 37;
  atualizarMoldura = (t, cena) => {
    num.textContent = pad(cena ? cena.n : 1, 3);
    tempo.textContent = relogio(inicioRec + t);
    tipo.textContent = cena ? `CENA ${pad(cena.n)} · ${(cena.visual.tipo || "").toUpperCase()}` : "";
    rec.style.opacity = (Math.floor(t * 1.6) % 2) ? 0.25 : 1;
    for (const q of pontos) {
      const y = (q.y - t * q.v) % 100;
      q.p.style.transform = `translate(${q.x * PW / 100}px, ${(y < 0 ? y + 100 : y) * PH / 100}px)`;
      q.p.style.opacity = 0.25 + 0.5 * (0.5 + 0.5 * Math.sin(t * 2 + q.f));
      q.p.style.width = q.p.style.height = q.s + "px";
    }
    fundo.querySelector(".varredura").style.transform = `translateY(${((t * 0.35) % 1.2 - 0.1) * PH}px)`;
  };
} else if (M.base === "estilo") {
  ACAB = window.instalarAcabamento(M.acabamento);
  fundo.innerHTML = ACAB.fundo ? ACAB.fundo(PW, PH) : "";
  moldura.innerHTML = ACAB.moldura ? ACAB.moldura() : "";
  if (M.marca) moldura.insertAdjacentHTML("beforeend", `<div class="rot r-sup-esq">${esc(M.marca)}</div>`);
  atualizarMoldura = (t, cena) => { if (ACAB.atualizar) ACAB.atualizar(t, cena, { fundo, moldura, PW, PH }); };
} else if (M.base === "rustico") {
  fundo.innerHTML = `<div class="papel"></div><div class="manchas"></div><div class="vinheta"></div>`;
  moldura.innerHTML = `<svg class="borda-mao" viewBox="0 0 1000 1000" preserveAspectRatio="none"><rect x="22" y="14" width="956" height="972" rx="6"/></svg>
    <div class="rot r-sup-esq">${esc(M.marca || "")}</div><div class="rot r-sup-dir">nº <span class="num">01</span></div>`;
  moldura.querySelector(".borda-mao").style.filter = "url(#rabisco)";
  const num = moldura.querySelector(".num");
  atualizarMoldura = (t, cena) => { num.textContent = pad(cena ? cena.n : 1); };
} else {
  fundo.innerHTML = `<div class="papel"></div><div class="vinheta"></div>`;
  moldura.innerHTML = `<div class="rot r-sup-esq">${esc(M.marca || "animatik")}<span class="arq">_v1</span></div>
    <div class="rot r-sup-dir"><span class="tempo">00:00:00:00</span></div>`;
  const tempo = moldura.querySelector(".tempo");
  atualizarMoldura = t => { tempo.textContent = relogio(t) + ":" + pad(Math.floor((t % 1) * 30)); };
}

// cursores "editando" (estilo papel): setinhas com etiqueta que passeiam pela tela
const cursores = [];
if (M.cursores) {
  const cores = ["#ff5c8a", "#3fb6ff", "#36c26b", "#ffb020"];
  const etiquetas = M.etiquetas_cursor || ["cena-01", "zoom-01", "legenda-02", "corte-03"];
  const rnd = aleatorio(11);
  etiquetas.forEach((nome, i) => {
    const c = el("div", "cursor", `<svg viewBox="0 0 24 24"><path d="M4 2l15 9-7 1.6-3.6 6.4z"/></svg><span>${esc(nome)}</span>`);
    c.style.setProperty("--cor", cores[i % cores.length]);
    cena3d.insertBefore(c, camadaCenas);  // passam por trás do texto e dos cards
    // só nas laterais e embaixo, longe do texto falado (que fica em cima, no meio)
    const alvos = Array.from({ length: 8 }, (_, k) => {
      const lado = (k + i) % 2 ? 0.06 + rnd() * 0.16 : 0.70 + rnd() * 0.16;
      return [lado, 0.34 + rnd() * 0.5];
    });
    cursores.push({ c, alvos, fase: rnd() * 3, vel: 0.22 + rnd() * 0.12 });
  });
}
function atualizarCursores(t, cena) {
  // na chamada final os cursores saem de cena (a palavra fica sozinha)
  const final = CENAS.find(c => c.cena.visual && c.cena.visual.tipo === "cta");
  const some = final ? 1 - prog(t, final.cena.ini, 0.4) : 1;
  for (const k of cursores) {
    const x = t * k.vel + k.fase, i = Math.floor(x), f = suave(x - i);
    const a = k.alvos[i % k.alvos.length], b = k.alvos[(i + 1) % k.alvos.length];
    k.c.style.transform = `translate(${misturar(a[0], b[0], f) * PW}px, ${misturar(a[1], b[1], f) * PH}px)`;
    k.c.style.opacity = lim((t - 0.6) * 2) * 0.95 * some;
  }
}

// ------------------------------------------------------------------ legenda (a fala da cena, palavra por palavra)
function montarLegenda(cena, caixa) {
  const leg = el("div", "legenda");
  const spans = [];
  for (const p of cena.palavras) {
    const s = el("span", "pal" + (p.dest ? " dest" : ""), esc(p.t));
    leg.appendChild(s); leg.appendChild(document.createTextNode(" "));
    spans.push([s, p]);
  }
  caixa.appendChild(leg);
  return (t) => {
    for (const [s, p] of spans) {
      const x = saida(prog(t, p.ini - 0.06, 0.22));
      s.style.opacity = x;
      s.style.transform = `translateY(${(1 - x) * 0.9}em)`;
      s.style.filter = x < 1 ? `blur(${(1 - x) * 8}px)` : "none";
      if (p.dest) s.classList.toggle("aceso", t >= p.ini);
    }
  };
}

// ------------------------------------------------------------------ efeitos sonoros
// cada animação avisa quando um som deve tocar; o Python lê a lista e monta a trilha de efeitos
const SONS = [];
let CENA_ATUAL = null;
const som = (offset, nome, extra = {}) => { if (CENA_ATUAL) SONS.push({ t: +(CENA_ATUAL.ini + offset).toFixed(3), som: nome, ...extra }); };

// ------------------------------------------------------------------ visuais
// Cada visual recebe (caixa, v = cena.visual, cena) e devolve atualizar(tl, dur), tl = tempo dentro da cena.
const VISUAIS = {};

VISUAIS.titulo = (caixa, v) => {
  const txt = String(v.texto || "").toUpperCase();
  const t0 = el("div", "v-titulo" + (v.riscar ? " riscavel" : ""));
  const tam = Math.max(7, Math.min(24, 120 / Math.max(3, txt.length)));
  t0.style.fontSize = `calc(var(--u) * ${tam})`;
  const letras = [...txt].map(ch => { const s = el("span", "letra", ch === " " ? "&nbsp;" : esc(ch)); t0.appendChild(s); return s; });
  let risco = null;
  if (v.riscar) { risco = el("i", "risco"); t0.appendChild(risco); }
  const aneis = el("div", "aneis", "<i></i><i></i><i></i>");
  caixa.append(aneis, t0);
  if (v.sub) caixa.appendChild(el("div", "v-sub", esc(v.sub)));
  const sub = caixa.querySelector(".v-sub");
  som(0.05, "impacto");
  if (v.riscar) som((CENA_ATUAL.fim - CENA_ATUAL.ini) * 0.45, "risco");
  return (tl, dur) => {
    letras.forEach((s, i) => {
      const x = mola(prog(tl, 0.05 + i * 0.045, 0.55));
      s.style.opacity = lim(x * 1.4);
      s.style.transform = `translateY(${(1 - x) * 40}%) scale(${misturar(1.6, 1, lim(x))})`;
      s.style.filter = x < 0.99 ? `blur(${(1 - lim(x)) * 14}px)` : "none";
    });
    const respira = 0.5 + 0.5 * Math.sin(tl * 3);
    t0.style.setProperty("--brilho", 0.6 + 0.4 * respira);
    if (risco) risco.style.transform = `scaleX(${saidaForte(prog(tl, dur * 0.45, 0.35))})`;
    aneis.querySelectorAll("i").forEach((a, i) => {
      const f = ((tl * 0.5 + i / 3) % 1);
      a.style.transform = `translate(-50%,-50%) scale(${0.4 + f * 1.4})`;
      a.style.opacity = (1 - f) * 0.5 * lim(tl * 2);
    });
    if (sub) { const x = saida(prog(tl, 0.5, 0.4)); sub.style.opacity = x; sub.style.transform = `translateY(${(1 - x) * 20}px)`; }
  };
};

VISUAIS.comando = (caixa, v) => {
  const txt = String(v.texto || "");
  const b = el("div", "v-comando painel", `
    <div class="cab"><i></i><i></i><i></i><span>${esc(v.titulo || "NOVO PEDIDO")}</span><em>${esc(v.rotulo || "")}</em></div>
    <div class="corpo"><span class="dig"></span><b class="cursor-txt">|</b></div>
    <div class="enviar">${icone("seta")}</div>`);
  caixa.appendChild(b);
  const dig = b.querySelector(".dig"), cur = b.querySelector(".cursor-txt"), env = b.querySelector(".enviar");
  const destaques = (v.destaque || []).map(s => s.toLowerCase());
  { const d = CENA_ATUAL.fim - CENA_ATUAL.ini; som(0.35, "digitar", { dur: +Math.max(0.8, d * 0.55).toFixed(2) }); som(0.35 + Math.max(0.8, d * 0.55), "pop"); }
  return (tl, dur) => {
    const ab = saida(prog(tl, 0, 0.35));
    b.style.opacity = ab; b.style.transform = `translateY(${(1 - ab) * 40}px) scale(${misturar(0.94, 1, ab)})`;
    const n = Math.floor(txt.length * prog(tl, 0.35, Math.max(0.8, dur * 0.55)));
    const parte = txt.slice(0, n);
    dig.innerHTML = destaques.length ? parte.split(/(\s+)/).map(w => destaques.includes(w.toLowerCase().replace(/[.,!?]/g, "")) ? `<mark>${esc(w)}</mark>` : esc(w)).join("") : esc(parte);
    cur.style.opacity = (Math.floor(tl * 2.5) % 2 || n < txt.length) ? 1 : 0;
    const e = prog(tl, 0.35 + Math.max(0.8, dur * 0.55), 0.3);
    env.style.transform = `scale(${1 + 0.25 * Math.sin(e * Math.PI)})`;
    env.classList.toggle("ativo", e > 0);
  };
};

VISUAIS.cards = (caixa, v) => {
  const itens = v.itens || [];
  const g = el("div", "v-cards n" + itens.length);
  const cs = itens.map((it, i) => {
    const c = el("div", "card painel", `<div class="ico-box">${icone(it.icone || "brilho")}</div><div class="rotulo">${esc(it.rotulo || "")}</div>${it.sub ? `<div class="mini">${esc(it.sub)}</div>` : ""}<span class="idx">${pad(i + 1)}</span>`);
    g.appendChild(c); return c;
  });
  caixa.appendChild(g);
  { const d = CENA_ATUAL.fim - CENA_ATUAL.ini, p = Math.min(0.32, (d * 0.6) / Math.max(1, cs.length)); cs.forEach((_, i) => som(0.1 + i * p, "pop", { tom: i })); }
  return (tl, dur) => {
    const passo = Math.min(0.32, (dur * 0.6) / Math.max(1, cs.length));
    cs.forEach((c, i) => {
      const x = mola(prog(tl, 0.1 + i * passo, 0.6));
      c.style.opacity = lim(x * 1.5);
      c.style.transform = `translateY(${(1 - x) * 60}px) scale(${misturar(0.7, 1, lim(x))}) rotate(${M.base === "papel" ? (i % 2 ? 1.5 : -1.5) * lim(x) : 0}deg)`;
      const ativo = Math.floor(prog(tl, 0.2 + cs.length * passo, dur * 0.8) * cs.length * 1.0001);
      c.classList.toggle("ativo", tl > 0.2 + cs.length * passo && ativo === i);
    });
  };
};

VISUAIS.fluxo = (caixa, v) => {
  const itens = v.itens || [];
  const f = el("div", "v-fluxo n" + itens.length);
  const nos = [], linhas = [];
  itens.forEach((it, i) => {
    if (i) { const l = el("div", "elo", "<i></i>"); f.appendChild(l); linhas.push(l.firstChild); }
    const n = el("div", "no painel", `${icone(it.icone || "brilho")}<span>${esc(it.rotulo || "")}</span>`);
    f.appendChild(n); nos.push(n);
  });
  caixa.appendChild(f);
  { const d = CENA_ATUAL.fim - CENA_ATUAL.ini, p = Math.min(0.55, (d * 0.75) / Math.max(1, nos.length)); nos.forEach((_, i) => som(0.1 + i * p, "pop", { tom: i })); }
  return (tl, dur) => {
    const passo = Math.min(0.55, (dur * 0.75) / Math.max(1, nos.length));
    nos.forEach((n, i) => {
      const x = mola(prog(tl, 0.1 + i * passo, 0.5));
      n.style.opacity = lim(x * 1.5);
      n.style.transform = `scale(${misturar(0.6, 1, lim(x))})`;
      n.classList.toggle("ativo", tl >= 0.1 + i * passo + 0.15);
      if (i) linhas[i - 1].style.transform = `scaleX(${saida(prog(tl, 0.1 + (i - 1) * passo + 0.2, passo - 0.1))})`;
    });
  };
};

VISUAIS.riscado = (caixa, v) => {
  const b = el("div", "v-riscado", `
    <div class="rotulo-peq">${esc(v.rotulo || "EM VEZ DE")}</div>
    <div class="antes painel">${v.icone ? icone(v.icone) : ""}<span>${esc(v.antes || "")}</span><i class="risco"></i></div>
    ${v.depois ? `<div class="depois painel">${icone(v.icone_depois || "check")}<span>${esc(v.depois)}</span></div>` : ""}`);
  caixa.appendChild(b);
  { const d = CENA_ATUAL.fim - CENA_ATUAL.ini; som(d * 0.35, "risco"); if (v.depois) som(d * 0.55, "pop", { tom: 3 }); }
  const rot = b.querySelector(".rotulo-peq"), antes = b.querySelector(".antes"), risco = b.querySelector(".risco"), depois = b.querySelector(".depois");
  return (tl, dur) => {
    const a = saida(prog(tl, 0, 0.35));
    rot.style.opacity = a;
    antes.style.opacity = a; antes.style.transform = `translateY(${(1 - a) * 30}px)`;
    const r = saidaForte(prog(tl, dur * 0.35, 0.3));
    risco.style.transform = `scaleX(${r})`;
    antes.style.filter = `grayscale(${r}) opacity(${1 - r * 0.45})`;
    if (depois) {
      const d = mola(prog(tl, dur * 0.55, 0.5));
      depois.style.opacity = lim(d * 1.5); depois.style.transform = `translateY(${(1 - d) * 40}px) scale(${misturar(0.8, 1, lim(d))})`;
    }
  };
};

VISUAIS.numero = (caixa, v) => {
  const alvo = parseFloat(String(v.valor ?? "0").replace(",", ".")) || 0;
  const casas = String(v.valor ?? "").includes(",") || String(v.valor ?? "").includes(".") ? 1 : 0;
  const b = el("div", "v-numero", `
    <svg class="anel" viewBox="0 0 200 200"><circle class="trilho" cx="100" cy="100" r="88"/><circle class="arco" cx="100" cy="100" r="88"/></svg>
    <div class="valor"><span class="n">0</span><small>${esc(v.sufixo || "")}</small></div>
    ${v.rotulo ? `<div class="rot-num">${esc(v.rotulo)}</div>` : ""}`);
  caixa.appendChild(b);
  const n = b.querySelector(".n"), arco = b.querySelector(".arco");
  const C = 2 * Math.PI * 88;
  arco.style.strokeDasharray = C;
  som(0.15, "subida", { dur: 1.1 }); som(1.25, "ding");
  return (tl) => {
    const a = saida(prog(tl, 0, 0.4));
    b.style.opacity = a; b.style.transform = `scale(${misturar(0.8, 1, a)})`;
    const x = saidaForte(prog(tl, 0.15, 1.1));
    n.textContent = (alvo * x).toFixed(casas).replace(".", ",");
    arco.style.strokeDashoffset = C * (1 - x * (v.porcento ? alvo / 100 : 1));
  };
};

VISUAIS.grafico = (caixa, v) => {
  const pts = v.pontos || [2, 3, 2.5, 3.2, 2.8, 3.5, 3, 9.5];
  const max = Math.max(...pts), N = pts.length;
  const coords = pts.map((p, i) => [10 + i * (380 / (N - 1)), 210 - (p / max) * 180]);
  const d = coords.map((c, i) => (i ? "L" : "M") + c[0].toFixed(1) + " " + c[1].toFixed(1)).join(" ");
  const b = el("div", "v-grafico painel", `
    <div class="cab"><i></i><i></i><i></i><span>${esc(v.titulo || "INTENSIDADE")}</span></div>
    <svg viewBox="0 0 400 230"><path class="eixo" d="M10 212 H390"/><path class="linha" d="${d}"/><path class="area" d="${d} L390 212 L10 212 Z"/>
      <circle class="ponto" r="9" cx="${coords[N - 1][0]}" cy="${coords[N - 1][1]}"/></svg>
    ${v.rotulo ? `<div class="etiqueta">${esc(v.rotulo)}</div>` : ""}`);
  caixa.appendChild(b);
  const linha = b.querySelector(".linha"), area = b.querySelector(".area"), ponto = b.querySelector(".ponto"), et = b.querySelector(".etiqueta");
  const L = linha.getTotalLength ? linha.getTotalLength() : 1200;
  linha.style.strokeDasharray = L;
  { const d = CENA_ATUAL.fim - CENA_ATUAL.ini, x = Math.max(0.8, d * 0.55); som(0.2, "subida", { dur: x }); som(0.2 + x, "pop", { tom: 4 }); }
  return (tl, dur) => {
    const a = saida(prog(tl, 0, 0.35));
    b.style.opacity = a; b.style.transform = `translateY(${(1 - a) * 40}px)`;
    const x = prog(tl, 0.2, Math.max(0.8, dur * 0.55));
    linha.style.strokeDashoffset = L * (1 - x);
    area.style.opacity = x * 0.35;
    const p = mola(prog(tl, 0.2 + Math.max(0.8, dur * 0.55), 0.5));
    ponto.style.transform = `scale(${p})`; ponto.style.transformOrigin = `${coords[N - 1][0]}px ${coords[N - 1][1]}px`;
    if (et) { et.style.opacity = lim(p * 1.4); et.style.transform = `translateY(${(1 - lim(p)) * 20}px) scale(${misturar(0.6, 1, lim(p))})`; }
  };
};

VISUAIS.lista = (caixa, v) => {
  const itens = v.itens || [];
  const l = el("div", "v-lista painel");
  const linhas = itens.map(it => {
    const r = el("div", "item", `<b class="caixa-check">${icone("check")}</b><span>${esc(typeof it === "string" ? it : it.rotulo)}</span>`);
    l.appendChild(r); return r;
  });
  caixa.appendChild(l);
  { const d = CENA_ATUAL.fim - CENA_ATUAL.ini, p = Math.min(0.6, (d * 0.7) / Math.max(1, linhas.length)); linhas.forEach((_, i) => som(0.45 + i * p, "check", { tom: i })); }
  return (tl, dur) => {
    const a = saida(prog(tl, 0, 0.3));
    l.style.opacity = a; l.style.transform = `translateY(${(1 - a) * 30}px)`;
    const passo = Math.min(0.6, (dur * 0.7) / Math.max(1, linhas.length));
    linhas.forEach((r, i) => {
      const x = saida(prog(tl, 0.15 + i * passo, 0.3));
      r.style.opacity = x; r.style.transform = `translateX(${(1 - x) * -30}px)`;
      r.classList.toggle("feito", tl > 0.15 + i * passo + 0.3);
    });
  };
};

VISUAIS.icone = (caixa, v) => {
  const b = el("div", "v-icone", `<div class="radar"><i></i><i></i><i></i></div><div class="bolha">${icone(v.icone || "brilho")}</div>${v.rotulo ? `<div class="rot-ico">${esc(v.rotulo)}</div>` : ""}`);
  caixa.appendChild(b);
  const bolha = b.querySelector(".bolha"), rot = b.querySelector(".rot-ico");
  som(0.05, "pop", { tom: 2 });
  return (tl) => {
    const x = mola(prog(tl, 0.05, 0.6));
    bolha.style.transform = `scale(${x}) rotate(${(1 - lim(x)) * -20}deg)`;
    bolha.style.opacity = lim(x * 1.5);
    b.querySelectorAll(".radar i").forEach((a, i) => {
      const f = ((tl * 0.6 + i / 3) % 1);
      a.style.transform = `translate(-50%,-50%) scale(${0.5 + f * 1.6})`;
      a.style.opacity = (1 - f) * 0.6 * lim(tl * 2);
    });
    if (rot) { const r = saida(prog(tl, 0.35, 0.4)); rot.style.opacity = r; rot.style.transform = `translateY(${(1 - r) * 20}px)`; }
  };
};

const AVATAR_PADRAO = `<svg viewBox="0 0 200 220" class="avatar-svg">
  <path class="ombro" d="M30 220c4-40 34-58 70-58s66 18 70 58"/>
  <path class="pescoco" d="M86 150v16c0 8 28 8 28 0v-16"/>
  <ellipse class="rosto" cx="100" cy="98" rx="50" ry="58"/>
  <path class="cabelo" d="M50 92c-6-42 22-66 52-64 34 2 54 24 48 62-6-16-14-26-26-30-20 8-46 8-66 0-4 10-6 20-8 32z"/>
  <path class="barba" d="M54 110c4 34 22 52 46 52s42-18 46-52c-8 12-20 18-46 18s-38-6-46-18z"/>
  <circle class="oculos" cx="80" cy="100" r="15"/><circle class="oculos" cx="120" cy="100" r="15"/><path class="oculos" d="M95 100h10M65 98l-14-4M135 98l14-4"/>
  <ellipse class="olho" cx="80" cy="101" rx="3.4" ry="4"/><ellipse class="olho" cx="120" cy="101" rx="3.4" ry="4"/>
  <path class="boca" d="M88 134c6 5 18 5 24 0"/></svg>`;

VISUAIS.avatar = (caixa, v) => {
  const img = M.avatar ? `<img src="${esc(M.avatar)}" class="avatar-img">` : AVATAR_PADRAO;
  const b = el("div", "v-avatar", `<div class="fig">${img}</div>${v.texto ? `<div class="balao painel">${esc(v.texto)}</div>` : ""}${v.etiqueta ? `<span class="tag-rev">${esc(v.etiqueta)}</span>` : ""}`);
  caixa.appendChild(b);
  som(0.05, "pop", { tom: 1 }); if (v.texto) som(0.35, "pop", { tom: 3 });
  const fig = b.querySelector(".fig"), balao = b.querySelector(".balao"), olhos = b.querySelectorAll(".olho");
  return (tl) => {
    const x = mola(prog(tl, 0.05, 0.6));
    fig.style.opacity = lim(x * 1.5);
    fig.style.transform = `translateY(${(1 - lim(x)) * 60 + Math.sin(tl * 2.2) * 4}px) scale(${misturar(0.85, 1, lim(x))})`;
    const pisca = (tl % 3.1) < 0.12;
    olhos.forEach(o => o.style.transform = `scaleY(${pisca ? 0.1 : 1})`);
    if (balao) { const y = mola(prog(tl, 0.35, 0.5)); balao.style.opacity = lim(y * 1.5); balao.style.transform = `scale(${misturar(0.6, 1, lim(y))})`; }
  };
};

VISUAIS.cta = (caixa, v) => {
  const b = el("div", "v-cta", `<div class="peq">${esc(v.rotulo || "COMENTA")}</div><div class="palavra">${esc(String(v.palavra || "").toUpperCase())}</div><div class="balao-ico">${icone("chat")}</div>`);
  caixa.appendChild(b);
  som(0.15, "impacto"); som(0.5, "pop", { tom: 4 });
  const peq = b.querySelector(".peq"), pal = b.querySelector(".palavra"), bi = b.querySelector(".balao-ico");
  return (tl) => {
    const a = saida(prog(tl, 0, 0.3)); peq.style.opacity = a;
    const x = mola(prog(tl, 0.15, 0.7));
    pal.style.opacity = lim(x * 1.4); pal.style.transform = `scale(${misturar(1.8, 1, lim(x))})`;
    pal.style.setProperty("--brilho", 0.7 + 0.3 * Math.sin(tl * 5));
    const y = mola(prog(tl, 0.5, 0.5));
    bi.style.transform = `translateY(${Math.sin(tl * 4) * 10}px) scale(${y})`;
  };
};

// ------------------------------------------------------------------ ilustração (desenho em SVG, animado)
// O desenho vem pronto no roteiro (campo "svg"). Cada elemento pode ter atributos de animação:
//   data-entra="esq|dir|cima|baixo|zoom|pop|cai|fade|desenha"  data-t="0.3" (início, s)  data-d="0.6" (duração)
//   data-mover="dx,dy" (anda isso durante a cena)   data-girar="graus por segundo"   data-balanca="graus"
//   data-tomba="85" + data-tomba-t="1.2" (cai deitado nessa hora)   data-pulsa="0.06" (aumenta e diminui)            data-som="motor|graos|pop|impacto|transicao|risco" (+ data-som-d)
(function rabisco() {
  // traço "feito à mão": o contorno treme um pouquinho, trocando a semente 8x por segundo (efeito de desenho animado)
  const defs = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  defs.setAttribute("width", "0"); defs.setAttribute("height", "0"); defs.style.position = "absolute";
  defs.innerHTML = `<filter id="rabisco" x="-5%" y="-5%" width="110%" height="110%">
    <feTurbulence id="rabisco-ruido" type="fractalNoise" baseFrequency="0.022" numOctaves="2" seed="1"/>
    <feDisplacementMap in="SourceGraphic" scale="${M.base === "estilo" ? ((window.ACABAMENTOS[M.acabamento] || {}).rabisco || 0) : (M.rabisco ?? 4)}" xChannelSelector="R" yChannelSelector="G"/></filter>`;
  document.body.appendChild(defs);
})();
const ruido = document.getElementById("rabisco-ruido");

VISUAIS.ilustracao = (caixa, v) => {
  const b = el("div", "v-ilustracao" + (v.moldura === false ? "" : " com-moldura"), v.svg || "");
  if (v.legenda_desenho) b.appendChild(el("div", "nota-desenho", esc(v.legenda_desenho)));
  caixa.appendChild(b);
  const svg = b.querySelector("svg");
  if (!svg) return () => {};
  svg.classList.add("desenho");
  const rab = ACAB ? (ACAB.rabisco ? "url(#rabisco) " : "") : (M.rabisco !== 0 && v.rabisco !== false ? "url(#rabisco) " : "");
  const filtroAcab = ACAB && ACAB.filtro ? ACAB.filtro : "";
  if (rab || filtroAcab) svg.style.filter = (rab + filtroAcab).trim();
  // estilos de traço (caderno, lousa, planta): tudo que não tem animação própria vai se desenhando, na ordem
  const autoTracos = [];
  if (ACAB && ACAB.desenharTudo) {
    const comAnim = new Set([...svg.querySelectorAll("[data-entra] *, [data-entra]")]);
    svg.querySelectorAll("path,line,polyline,polygon,circle,ellipse,rect").forEach(p => {
      if (comAnim.has(p)) return;
      p.setAttribute("pathLength", "1"); p.style.strokeDasharray = "1"; autoTracos.push(p);
    });
  }
  const itens = [...svg.querySelectorAll("[data-entra],[data-mover],[data-girar],[data-balanca],[data-pulsa],[data-som],[data-tomba]")].map(e => {
    const it = { e, entra: e.dataset.entra, t: +(e.dataset.t ?? 0.1), d: +(e.dataset.d ?? 0.6),
      mover: e.dataset.mover ? e.dataset.mover.split(",").map(Number) : null, girar: +(e.dataset.girar || 0),
      balanca: +(e.dataset.balanca || 0), pulsa: +(e.dataset.pulsa || 0),
      tomba: +(e.dataset.tomba || 0), tombaT: +(e.dataset.tombaT || 0) };
    e.style.transformBox = "fill-box"; e.style.transformOrigin = e.dataset.origem || "center";
    if (it.entra === "desenha") {
      it.tracos = [...(e.matches("path,line,polyline,polygon,circle,ellipse,rect") ? [e] : []),
                   ...e.querySelectorAll("path,line,polyline,polygon,circle,ellipse,rect")];
      it.tracos.forEach(p => { p.setAttribute("pathLength", "1"); p.style.strokeDasharray = "1"; p.dataset.fillop = p.getAttribute("fill-opacity") || "1"; });
    }
    if (e.dataset.som) som(it.t, e.dataset.som, e.dataset.somD ? { dur: +e.dataset.somD } : {});
    return it;
  });
  return (tl, dur) => {
    if (autoTracos.length) {
      const janela = Math.min(1.6, dur * 0.55), passo = janela / autoTracos.length;
      autoTracos.forEach((p, i) => { p.style.strokeDashoffset = 1 - saida(prog(tl, i * passo * 0.7, Math.max(0.25, passo * 3))); });
    }
    for (const it of itens) {
      const x = prog(tl, it.t, it.d);
      let tx = 0, ty = 0, sc = 1, rot = 0, op = 1;
      switch (it.entra) {
        case "esq": tx = -(1 - saida(x)) * 700; op = lim(x * 3); break;
        case "dir": tx = (1 - saida(x)) * 700; op = lim(x * 3); break;
        case "cima": ty = -(1 - saida(x)) * 500; op = lim(x * 3); break;
        case "baixo": ty = (1 - saida(x)) * 500; op = lim(x * 3); break;
        case "zoom": sc = misturar(0.4, 1, saida(x)); op = lim(x * 2); break;
        case "pop": sc = mola(x); op = lim(x * 4); break;
        case "cai": { const y = x < 1 ? 1 - Math.abs(Math.cos(x * Math.PI * 1.5)) * (1 - x) : 1; ty = -(1 - y) * 300 * (x < 0.33 ? 1 : 0.4); op = lim(x * 4); break; }
        case "fade": op = suave(x); break;
        case "desenha":
          it.tracos.forEach(p => { p.style.strokeDashoffset = 1 - lim(x * 1.25); p.style.fillOpacity = lim((x - 0.55) / 0.45) * +p.dataset.fillop; });
          break;
      }
      if (it.mover) { const m = suave(prog(tl, it.t, Math.max(0.5, dur - it.t))); tx += it.mover[0] * m; ty += it.mover[1] * m; }
      if (it.girar) rot += it.girar * tl;
      if (it.balanca) rot += it.balanca * Math.sin(tl * 2.4 + (it.e.dataset.fase ? +it.e.dataset.fase : 0));
      if (it.pulsa) sc *= 1 + it.pulsa * Math.sin(tl * 6);
      if (it.tomba) rot += it.tomba * saidaForte(prog(tl, it.tombaT, 0.45));
      it.e.style.transform = `translate(${tx}px, ${ty}px) rotate(${rot}deg) scale(${sc})`;
      if (it.entra !== "desenha") it.e.style.opacity = op;
    }
  };
};

VISUAIS.nada = () => () => {};

// ------------------------------------------------------------------ montar as cenas
const CENAS = D.cenas.map((cena, i) => {
  const box = el("div", "cena");
  camadaCenas.appendChild(box);
  const topo = el("div", "topo-cena");
  const meio = el("div", "meio-cena");
  const interno = el("div", "interno");
  meio.appendChild(interno);
  box.append(topo, meio);
  const tipo = (cena.visual && cena.visual.tipo) || "nada";
  CENA_ATUAL = cena;
  if (i > 0) som(-0.05, "transicao");
  if (tipo === "titulo" && !cena.legenda_junto) box.classList.add("so-titulo");
  const legenda = montarLegenda(cena, topo);
  const visual = (VISUAIS[tipo] || VISUAIS.nada)(interno, cena.visual || {}, cena);
  return { cena, box, meio, interno, legenda, visual, ajustado: false };
});

function ajustar(c) {
  // o visual nunca passa da área do meio: diminui se precisar
  c.interno.style.transform = "none";
  const disp = c.meio.getBoundingClientRect(), nat = c.interno.getBoundingClientRect();
  const k = Math.min(1, (disp.width * 0.94) / Math.max(1, nat.width), (disp.height * 0.94) / Math.max(1, nat.height));
  c.escala = k;
  c.ajustado = true;
}

// ------------------------------------------------------------------ desenhar um instante
const TRANS = 0.28; // segundos da transição entre cenas
function desenhar(t) {
  let atual = null;
  for (const c of CENAS) {
    const { ini, fim } = c.cena;
    const visivel = t >= ini - 0.001 && t < fim + TRANS;
    c.box.style.display = visivel ? "flex" : "none";
    if (!visivel) continue;
    if (!c.ajustado) ajustar(c);
    if (t < fim) atual = c.cena;
    const tl = t - ini, dur = fim - ini;
    const ent = saida(prog(tl, 0, TRANS)), sai = prog(t, fim, TRANS);
    const sobe = M.base === "neon" ? 1 : 0.6;
    c.box.style.opacity = ent * (1 - sai);
    c.box.style.transform = `translateY(${(1 - ent) * 40 * sobe - saida(sai) * 60 * sobe}px) scale(${misturar(1.04, 1, ent) * misturar(1, 0.97, sai)})`;
    c.interno.style.transform = `scale(${c.escala * misturar(1, 1.035, prog(tl, 0, dur))})`;
    c.legenda(t);
    const q = ACAB && ACAB.quadros ? ACAB.quadros : 0;
    c.visual(q ? Math.floor(tl * q) / q : tl, dur);
  }
  // flash rápido na troca de cena (neon) / nada no papel
  let fl = 0;
  if (M.base === "neon") for (const c of CENAS) { const d = t - c.cena.ini; if (d >= 0 && d < 0.14) fl = Math.max(fl, (1 - d / 0.14) * 0.1); }
  flash.style.opacity = fl;
  // câmera: aproximação lenta e respiração
  const z = 1 + 0.015 * Math.sin(t * 0.5);
  cena3d.style.transform = `scale(${z}) translate(${Math.sin(t * 0.7) * 3}px, ${Math.cos(t * 0.6) * 3}px)`;
  if (ruido) ruido.setAttribute("seed", String(1 + (Math.floor(t * (ACAB && ACAB.quadros ? ACAB.quadros : 8)) % 4)));
  atualizarMoldura(t, atual);
  atualizarCursores(t, atual);
  if (M.formato === "monitor") atualizarMonitor(t);
}

// ------------------------------------------------------------------ formato "monitor" (vídeo filmando a tela)
let atualizarMonitor = () => {};
if (M.formato === "monitor") {
  const sala = document.getElementById("sala");
  const topo = document.getElementById("faixa-topo");
  if (M.topo_texto) { topo.textContent = M.topo_texto; topo.style.display = "block"; }
  atualizarMonitor = t => {
    // celular na mão: tremidinha suave
    const x = Math.sin(t * 1.3) * 3 + Math.sin(t * 3.1) * 1.2, y = Math.cos(t * 1.1) * 3 + Math.sin(t * 2.3);
    sala.style.transform = `translate(${x}px, ${y}px) rotate(${Math.sin(t * 0.8) * 0.25}deg) scale(1.01)`;
  };
}

window.desenhar = desenhar;
window.SONS = SONS;
window.PRONTO = document.fonts.ready.then(() => { desenhar(0); return true; });
