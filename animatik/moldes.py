"""
Moldes = estilos de vídeo. Cada molde é uma pasta em moldes/<nome>/ com:
  molde.json   cores, fontes, tipo de animação, voz, música e o jeito do roteiro (tom, gancho, chamada)
  exemplos/    os vídeos de exemplo que você mandou (se o molde foi criado a partir deles)
  avatar.png   (opcional) o seu avatar, aparece nas cenas de avatar
  amostra.jpg  como o molde fica (gerado sozinho)

Criar molde a partir de exemplos: o Animatik tira quadros dos vídeos e o Claude (com a chave da API)
descreve o estilo: cores, clima, ritmo, tipo de texto, gancho e chamada. Isso vira um molde novo.
"""
import base64
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from .util import MOLDES, duracao, ler_json, log, salvar_json

BASES = {"neon": "fundo escuro, cara de tela de sistema/terminal, cor de destaque com brilho, cantinhos e rótulos técnicos",
         "papel": "fundo claro de papel, texto escuro, destaque em itálico de caneta, avatar desenhado, ar de caderno/editorial"}


def _slug(nome: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFD", nome.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:40] or "molde"


def listar() -> list[dict]:
    saida = []
    for p in sorted(MOLDES.iterdir()) if MOLDES.is_dir() else []:
        m = ler_json(p / "molde.json")
        if not m:
            continue
        saida.append({"id": p.name, "nome": m.get("nome", p.name), "descricao": m.get("descricao", ""), "base": m.get("base"),
                      "cores": m.get("cores", {}), "amostra": (p / "amostra.jpg").exists(),
                      "exemplos": len(list((p / "exemplos").glob("*"))) if (p / "exemplos").is_dir() else 0,
                      "formato": m.get("formato", "vertical"), "voz": m.get("voz"), "marca": m.get("marca", "")})
    return saida


def carregar_molde(nome: str) -> dict:
    pasta = MOLDES / nome
    m = ler_json(pasta / "molde.json")
    if not m:
        raise ValueError(f"molde '{nome}' não encontrado")
    m = dict(m)
    av = pasta / "avatar.png"
    if av.exists():  # o navegador do gravador abre o arquivo direto
        m["avatar"] = av.as_uri()
    elif m.get("avatar") and not str(m["avatar"]).startswith(("file:", "data:", "http")):
        m["avatar"] = ""
    m.setdefault("semente", sum(map(ord, nome)) % 97)
    return m


def salvar_molde(nome: str, dados: dict) -> None:
    salvar_json(MOLDES / nome / "molde.json", dados)


def duplicar(origem: str, novo_nome: str) -> str:
    novo = _slug(novo_nome)
    i = 2
    while (MOLDES / novo).exists():
        novo = f"{_slug(novo_nome)}-{i}"
        i += 1
    shutil.copytree(MOLDES / origem, MOLDES / novo, ignore=shutil.ignore_patterns("exemplos", "amostra.jpg"))
    m = ler_json(MOLDES / novo / "molde.json")
    m["nome"] = novo_nome
    salvar_molde(novo, m)
    return novo


# ------------------------------------------------------------------ analisar exemplos
def _quadros(video: Path, n: int = 8) -> list[bytes]:
    dur = duracao(video) or 30
    fotos = []
    with tempfile.TemporaryDirectory() as tmp:
        for i in range(n):
            t = dur * (i + 0.5) / n
            saida = Path(tmp) / f"q{i}.jpg"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1",
                            "-vf", "scale=-2:768", "-q:v", "4", str(saida)])
            if saida.exists():
                fotos.append(saida.read_bytes())
    return fotos


def _cortes_por_minuto(video: Path) -> float:
    r = subprocess.run(["ffmpeg", "-i", str(video), "-vf", "select='gt(scene,0.3)',showinfo", "-f", "null", "-"],
                       capture_output=True, text=True)
    n = r.stderr.count("pts_time:")
    return round(n / max(1e-3, (duracao(video) or 60) / 60), 1)


COR = {"type": "string", "description": "cor em hex, ex. #3dff6e"}
ESQUEMA_MOLDE = {
    "type": "object", "additionalProperties": False,
    "required": ["nome", "descricao", "base", "cores", "formato", "cursores", "marca", "musica", "voz_genero", "roteiro"],
    "properties": {
        "nome": {"type": "string"}, "descricao": {"type": "string"},
        "base": {"type": "string", "enum": list(BASES)},
        "cores": {"type": "object", "additionalProperties": False,
                  "required": ["fundo", "texto", "destaque", "destaque2"],
                  "properties": {"fundo": COR, "fundo2": COR, "texto": COR, "destaque": COR, "destaque2": COR}},
        "formato": {"type": "string", "enum": ["vertical", "monitor"]},
        "topo_texto": {"type": "string"},
        "cursores": {"type": "boolean"},
        "marca": {"type": "string"},
        "musica": {"type": "string", "enum": ["pulso", "lofi"]},
        "voz_genero": {"type": "string", "enum": ["masculina", "feminina"]},
        "roteiro": {"type": "object", "additionalProperties": False,
                    "required": ["tom", "gancho", "cta", "duracao_seg", "visuais_preferidos"],
                    "properties": {"tom": {"type": "string"}, "gancho": {"type": "string"}, "cta": {"type": "string"},
                                   "duracao_seg": {"type": "integer"},
                                   "visuais_preferidos": {"type": "array", "items": {"type": "string", "enum": [
                                       "titulo", "comando", "cards", "fluxo", "riscado", "numero", "grafico", "lista",
                                       "icone", "avatar", "cta"]}}}},
    },
}


def analisar_exemplos(videos: list[Path], nome: str, cfg_ia: dict) -> dict:
    """Manda quadros dos exemplos para o Claude e recebe o molde (JSON)."""
    from .roteiro import _pedir_json
    conteudo = []
    for k, v in enumerate(videos[:3]):
        info = f"Exemplo {k + 1}: {duracao(v):.0f}s, {_cortes_por_minuto(v)} cortes bruscos por minuto. Quadros em ordem:"
        conteudo.append({"type": "text", "text": info})
        for q in _quadros(v):
            conteudo.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                                         "data": base64.standard_b64encode(q).decode()}})
    conteudo.append({"type": "text", "text": (
        f"Crie um molde chamado \"{nome}\" que reproduza o estilo VISUAL e o jeito de falar desses exemplos.\n"
        "O Animatik faz vídeos verticais de motion design (texto animado, cards, ícones, avatar desenhado) a partir de "
        "uma narração por voz de IA. Ele tem duas bases visuais; escolha a mais próxima e ajuste as cores:\n"
        + "\n".join(f"- {k}: {d}" for k, d in BASES.items()) +
        "\nformato: 'monitor' se os exemplos mostram a animação numa tela filmada (monitor/notebook na mesa); senão 'vertical'.\n"
        "topo_texto: se houver uma faixa fixa de texto em cima do vídeo (tipo 'Vídeo feito com IA'), copie a ideia; senão vazio.\n"
        "cursores: true se aparecem setinhas de mouse com etiquetas 'editando'.\n"
        "marca: rótulo curto que aparece no canto (ex.: nome do projeto), em minúsculas ou MAIÚSCULAS conforme o estilo.\n"
        "cores: tire dos quadros (hex). destaque = a cor das palavras-chave; destaque2 = cor de alerta/risco.\n"
        "roteiro.tom e roteiro.gancho: descreva como o narrador fala e como o vídeo começa (pelo texto na tela).\n"
        "roteiro.cta: o formato da chamada final, com {PALAVRA} no lugar da palavra (ex.: 'Comenta {PALAVRA}').\n"
        "roteiro.duracao_seg: duração típica dos exemplos.\n"
        "visuais_preferidos: os tipos de cena do Animatik que mais lembram o que aparece nos exemplos.")})
    sistema = "Você é diretor de arte de vídeos curtos e descreve estilos de forma objetiva para um gerador automático."
    return _pedir_json(cfg_ia, sistema, conteudo, ESQUEMA_MOLDE)


def criar_de_exemplos(nome: str, arquivos: list[Path], cfg_ia: dict) -> str:
    """Cria a pasta do molde, guarda os exemplos e preenche o molde.json com a análise."""
    from .roteiro import tem_chave
    if not tem_chave():
        raise RuntimeError("Para ler o estilo dos exemplos, o Animatik precisa da chave da API do Claude "
                           "(veja o LEIA-ME). Sem ela, use um dos moldes prontos e ajuste as cores.")
    slug = _slug(nome)
    i = 2
    while (MOLDES / slug).exists():
        slug = f"{_slug(nome)}-{i}"
        i += 1
    pasta = MOLDES / slug
    (pasta / "exemplos").mkdir(parents=True)
    guardados = []
    for a in arquivos:
        destino = pasta / "exemplos" / Path(a).name
        shutil.copy2(a, destino)
        guardados.append(destino)
    try:
        analise = analisar_exemplos(guardados, nome, cfg_ia)
    except Exception:
        shutil.rmtree(pasta, ignore_errors=True)
        raise
    base = carregar_molde(analise["base"]) if (MOLDES / analise["base"]).exists() else {}
    molde = {**{k: v for k, v in base.items() if k not in ("avatar", "semente")}, **analise}
    molde["nome"] = nome
    # linha/suave/fundo2 do molde base são da cor dele: saem fora e o motor calcula a partir das cores novas
    molde["cores"] = {k: v for k, v in {**base.get("cores", {}), **analise["cores"]}.items()
                      if k in analise["cores"] or k not in ("linha", "suave", "fundo2")}
    molde["voz"] = "pt-BR-FranciscaNeural" if analise.get("voz_genero") == "feminina" else "pt-BR-AntonioNeural"
    molde.pop("voz_genero", None)
    salvar_molde(slug, molde)
    log.info("molde criado: %s", json.dumps(molde, ensure_ascii=False)[:400])
    return slug
