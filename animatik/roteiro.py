"""
Roteiro do vídeo: a fala dividida em cenas, cada cena com um visual animado.

- Com a chave da API do Claude (ANTHROPIC_API_KEY): o Claude escreve o roteiro a partir do tema, no tom do molde.
- Sem chave: você escreve (ou cola) o texto e o Animatik divide em cenas e escolhe os visuais sozinho.
  Marque palavras com *asteriscos* para destacar. Ex.: "Isso aqui é *código*."
"""
import json
import os
import re

from .util import log

ICONES = ["live", "chat", "play", "tesoura", "legenda", "musica", "raio", "relogio", "codigo", "microfone", "texto", "filme",
          "check", "estrela", "pessoa", "pasta", "olho", "fogo", "grafico", "engrenagem", "robo", "celular", "coracao",
          "brilho", "camera", "lapis", "download", "ia", "dinheiro", "seta", "x", "mundo", "cadeado", "foguete", "joystick"]
TIPOS = ["titulo", "comando", "cards", "fluxo", "riscado", "numero", "grafico", "lista", "icone", "avatar", "cta"]

ITEM = {"type": "object", "additionalProperties": False, "required": ["rotulo", "icone"],
        "properties": {"rotulo": {"type": "string"}, "icone": {"type": "string", "enum": ICONES}, "sub": {"type": "string"}}}
VISUAL = {
    "type": "object", "additionalProperties": False, "required": ["tipo"],
    "properties": {
        "tipo": {"type": "string", "enum": TIPOS},
        "texto": {"type": "string"}, "sub": {"type": "string"}, "riscar": {"type": "boolean"},
        "titulo": {"type": "string"}, "rotulo": {"type": "string"},
        "destaque": {"type": "array", "items": {"type": "string"}},
        "itens": {"type": "array", "items": ITEM},
        "antes": {"type": "string"}, "depois": {"type": "string"},
        "icone": {"type": "string", "enum": ICONES}, "icone_depois": {"type": "string", "enum": ICONES},
        "valor": {"type": "string"}, "sufixo": {"type": "string"}, "porcento": {"type": "boolean"},
        "pontos": {"type": "array", "items": {"type": "number"}},
        "palavra": {"type": "string"}, "etiqueta": {"type": "string"},
    },
}
ESQUEMA = {
    "type": "object", "additionalProperties": False, "required": ["titulo", "legenda_post", "cenas"],
    "properties": {
        "titulo": {"type": "string"},
        "legenda_post": {"type": "string"},
        "cenas": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["fala", "visual"],
            "properties": {"fala": {"type": "string"}, "visual": VISUAL}}},
    },
}

GUIA_VISUAIS = """Visuais disponíveis (campo "visual"):
- titulo: palavra ou expressão GIGANTE (texto, até ~12 letras). "riscar": true risca a palavra (para negar algo). "sub": linha pequena embaixo.
- comando: caixa de pedido/terminal sendo digitada (texto = o que é digitado, curto; titulo = cabeçalho tipo "NOVO PEDIDO"; destaque = palavras do texto em cor).
- cards: 2 a 4 cartões com ícone e rótulo curto (itens).
- fluxo: 2 a 4 etapas ligadas por linha, de cima para baixo (itens), para mostrar processo "A → B → C".
- riscado: "em vez de" (rotulo opcional), "antes" é riscado, "depois" aparece embaixo.
- numero: número grande contando (valor, ex "2" ou "98"; sufixo ex "min", "%", "x"; porcento true se for %; rotulo embaixo).
- grafico: linha subindo com pico no fim (pontos opcionais; rotulo ex "x10"; titulo ex "VIEWS").
- lista: 2 a 4 itens com check sendo marcados (itens com rotulo).
- icone: um ícone grande pulsando (icone; rotulo curto).
- avatar: o boneco do apresentador (texto = balão de fala curto, opcional).
- cta: chamada final (palavra = a palavra que a pessoa deve comentar; rotulo ex "COMENTA").
Ícones: """ + ", ".join(ICONES)


def tem_chave() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))


def _cliente():
    import anthropic
    return anthropic.Anthropic()


def _pedir_json(cfg_ia: dict, sistema: str, conteudo, esquema: dict, max_tokens: int = 16000) -> dict:
    """Uma chamada ao Claude que devolve JSON no formato do esquema."""
    import anthropic
    cliente = _cliente()
    pedido = dict(
        model=cfg_ia.get("modelo", "claude-opus-5-5"),
        max_tokens=max_tokens,
        system=sistema,
        messages=[{"role": "user", "content": conteudo}],
        output_config={"effort": cfg_ia.get("esforco", "medium"),
                       "format": {"type": "json_schema", "schema": esquema}},
    )
    try:
        # se o modelo recusar o pedido, a própria API tenta de novo com outro modelo
        r = cliente.beta.messages.create(**pedido, betas=["server-side-fallback-2026-07-01"], fallbacks="default")
    except (anthropic.BadRequestError, TypeError) as e:  # versão da API/SDK sem fallback: pede do jeito simples
        log.info("pedido sem fallback (%s)", getattr(e, "message", e))
        r = cliente.messages.create(**pedido)
    if r.stop_reason == "refusal":
        raise RuntimeError("o Claude recusou esse tema. Tente outro tema ou escreva o texto você mesmo.")
    if r.stop_reason == "max_tokens":
        raise RuntimeError("a resposta do Claude ficou grande demais; tente um vídeo mais curto")
    texto = next(b.text for b in r.content if b.type == "text")
    return json.loads(texto)


def gerar_roteiro(tema: str, molde: dict, cfg_ia: dict, duracao: int | None = None, palavra_cta: str = "") -> dict:
    """O Claude escreve o roteiro completo (fala + visual de cada cena) no estilo do molde."""
    r = molde.get("roteiro", {})
    dur = int(duracao or r.get("duracao_seg", 40))
    palavras = int(dur * 2.6)  # ~2,6 palavras por segundo com a voz um pouco acelerada
    visuais = r.get("visuais_preferidos") or TIPOS
    sistema = (
        "Você escreve roteiros de vídeos curtos verticais (Reels/TikTok) em português do Brasil, narrados por voz, "
        "em que cada frase vira uma cena animada (motion design com texto e ícones, sem fotos).\n"
        "Regras:\n"
        f"- Total de cerca de {palavras} palavras faladas (~{dur} segundos). Entre 7 e 14 cenas.\n"
        "- Cada cena tem UMA frase curta (4 a 14 palavras), falada naturalmente. A fala aparece escrita na tela,\n"
        "  então marque com *asteriscos* 1 ou 2 palavras-chave por cena (ex.: 'Isso aqui é *código*.').\n"
        "- A 1ª cena é o gancho: prende a atenção nos 2 primeiros segundos.\n"
        "- A última cena é a chamada (visual cta) pedindo para comentar uma palavra.\n"
        "- Escreva números por extenso quando forem falados de forma diferente do que se lê (ex.: 'dois minutos').\n"
        "- Varie os visuais: não repita o mesmo tipo em cenas seguidas. Textos dentro dos visuais são CURTOS.\n"
        "- legenda_post: texto para a legenda do post, com 3 a 6 hashtags no fim.\n"
        f"Tom: {r.get('tom', 'direto e simples')}.\nGancho: {r.get('gancho', 'forte')}.\n"
        f"Chamada final: {r.get('cta', 'Comenta {PALAVRA}')}.\n"
        f"Visuais que combinam com este estilo (prefira estes): {', '.join(visuais)}.\n\n" + GUIA_VISUAIS
    )
    pedido = f"Tema do vídeo: {tema.strip()}"
    if palavra_cta:
        pedido += f"\nPalavra da chamada final: {palavra_cta.strip().upper()}"
    return _pedir_json(cfg_ia, sistema, pedido, ESQUEMA)


# ------------------------------------------------------------------ sem chave: texto -> cenas por regras
def _frases(texto: str) -> list[str]:
    linhas = [l.strip() for l in texto.replace("\r", "").split("\n") if l.strip()]
    frases = []
    for l in linhas:
        partes = re.split(r"(?<=[.!?…])\s+", l)
        frases += [p.strip() for p in partes if p.strip()]
    # junta frases muito curtas com a próxima; quebra frases muito longas na vírgula
    saida = []
    for f in frases:
        if saida and len(saida[-1].split()) < 4:
            saida[-1] += " " + f
        elif len(f.split()) > 16 and "," in f:
            meio = f.split(",")
            saida += [m.strip() + ("," if i < len(meio) - 1 else "") for i, m in enumerate(meio) if m.strip()]
        else:
            saida.append(f)
    return saida


PALAVRAS_ICONE = {
    "live": "live", "ao vivo": "live", "chat": "chat", "coment": "chat", "vídeo": "play", "video": "play", "corte": "tesoura",
    "legenda": "legenda", "música": "musica", "musica": "musica", "rápido": "raio", "minuto": "relogio", "hora": "relogio",
    "tempo": "relogio", "código": "codigo", "codigo": "codigo", "voz": "microfone", "narra": "microfone", "texto": "texto",
    "film": "filme", "pronto": "check", "pessoa": "pessoa", "seguidor": "pessoa", "pasta": "pasta", "arquivo": "pasta",
    "view": "olho", "assist": "olho", "viral": "fogo", "cresc": "grafico", "robô": "robo", "robo": "robo", "celular": "celular",
    "ia": "ia", "inteligência": "ia", "dinheiro": "dinheiro", "grátis": "dinheiro", "jogo": "joystick", "gta": "joystick",
    "câmera": "camera", "edit": "lapis", "baix": "download", "segur": "cadeado", "lança": "foguete",
}


def _icone_para(texto: str) -> str:
    t = texto.lower()
    for chave, ico in PALAVRAS_ICONE.items():
        if chave in t:
            return ico
    return "brilho"


def _destaques(frase: str) -> list[str]:
    return [m.strip(".,!?:;") for m in re.findall(r"\*([^*]+)\*", frase)]


def roteiro_de_texto(texto: str, palavra_cta: str = "", base: str = "neon") -> dict:
    """Divide um texto em cenas e escolhe um visual para cada uma (sem IA)."""
    frases = _frases(texto)
    cenas = []
    ciclo = ["cards", "icone", "titulo", "fluxo", "lista"] if base == "neon" else ["avatar", "titulo", "icone", "cards", "lista"]
    k = 0
    for i, f in enumerate(frases):
        limpa = f.replace("*", "")
        dest = _destaques(f)
        palavras = [p.strip(".,!?:;…") for p in limpa.split()]
        longa = max(palavras, key=len) if palavras else ""
        numero = re.search(r"\b(\d+[\d.,]*)\s*(%|x|min|minutos|horas|mil|k)?", limpa, re.I)
        if i == 0:
            v = {"tipo": "titulo", "texto": (dest[0] if dest else longa)[:14]}
        elif re.search(r"\bem vez de\b|\bem vez\b|\bao invés\b|\bsem\b", limpa, re.I):
            depois = limpa.split(",")[-1].strip(" .") if "," in limpa else ""
            antes = re.split(r"em vez de|ao invés de|sem", limpa, flags=re.I)[-1].split(",")[0].strip(" .")
            v = {"tipo": "riscado", "antes": antes[:28], "depois": depois[:28]}
        elif numero:
            suf = (numero.group(2) or "").lower()
            suf = {"minutos": "min", "horas": "h"}.get(suf, suf)
            v = {"tipo": "numero", "valor": numero.group(1), "sufixo": suf, "porcento": suf == "%"}
        elif "→" in f or "->" in f:
            partes = [p.strip(" .*") for p in re.split(r"→|->", limpa) if p.strip()]
            v = {"tipo": "fluxo", "itens": [{"rotulo": p[:18], "icone": _icone_para(p)} for p in partes[:4]]}
        elif re.match(r"^(digit|escrev|pede|pedi|fala pra|manda)", limpa, re.I) and '"' in limpa:
            v = {"tipo": "comando", "texto": limpa.split('"')[1], "titulo": "NOVO PEDIDO"}
        else:
            tipo = ciclo[k % len(ciclo)]
            k += 1
            chaves = dest or sorted(palavras, key=len, reverse=True)[:3]
            if tipo == "cards":
                v = {"tipo": "cards", "itens": [{"rotulo": c[:16], "icone": _icone_para(c)} for c in chaves[:3]]}
            elif tipo == "fluxo":
                v = {"tipo": "fluxo", "itens": [{"rotulo": c[:16], "icone": _icone_para(c)} for c in chaves[:3]]}
            elif tipo == "lista":
                v = {"tipo": "lista", "itens": [c[:22] for c in chaves[:3]]}
            elif tipo == "icone":
                v = {"tipo": "icone", "icone": _icone_para(limpa), "rotulo": (dest[0] if dest else longa)[:18]}
            elif tipo == "avatar":
                v = {"tipo": "avatar"}
            else:
                v = {"tipo": "titulo", "texto": (dest[0] if dest else longa)[:14]}
        cenas.append({"fala": f, "visual": v})
    if palavra_cta:
        cenas.append({"fala": f"Comenta *{palavra_cta.upper()}* que eu te mando.", "visual": {"tipo": "cta", "palavra": palavra_cta.upper()}})
    elif cenas and re.search(r"comenta", cenas[-1]["fala"], re.I):
        m = re.search(r"comenta\s+\*?([\wÀ-ú]+)", cenas[-1]["fala"], re.I)
        cenas[-1]["visual"] = {"tipo": "cta", "palavra": (m.group(1) if m else "EU").upper()}
    return {"titulo": frases[0].replace("*", "")[:60] if frases else "vídeo", "legenda_post": "", "cenas": cenas}
