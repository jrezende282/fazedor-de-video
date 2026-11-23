"""Painel do Animatik: criar vídeos, ver a biblioteca e cuidar dos moldes (estilos)."""
import base64
import os
import queue
import secrets
import shutil
import tempfile
import threading
import time
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import moldes as M
from .produzir import Andamento, novo_id, previa, produzir
from .roteiro import gerar_roteiro, roteiro_de_texto, tem_chave
from .util import MOLDES, VIDEOS, WEB, carregar_config, ler_json, log, salvar_json
from .voz import VOZES

app = FastAPI(title="Animatik")
VIDEOS.mkdir(parents=True, exist_ok=True)
app.mount("/midia", StaticFiles(directory=VIDEOS), name="midia")
app.mount("/web", StaticFiles(directory=WEB), name="web")
CFG = carregar_config()
FILA: queue.Queue = queue.Queue()
TAREFAS: dict[str, dict] = {}  # tarefas de molde (análise dos exemplos)


@app.middleware("http")
async def senha(request: Request, call_next):
    """Se PAINEL_SENHA estiver definida, o painel pede senha (usuário qualquer)."""
    esperada = os.environ.get("PAINEL_SENHA")
    if esperada:
        cab = request.headers.get("authorization", "")
        ok = False
        if cab.startswith("Basic "):
            try:
                ok = secrets.compare_digest(base64.b64decode(cab[6:]).decode().partition(":")[2], esperada)
            except Exception:
                ok = False
        if not ok:
            return Response(status_code=401, headers={"WWW-Authenticate": 'Basic realm="Animatik"'})
    return await call_next(request)


def trabalhador():
    """Produz um vídeo por vez (renderizar usa bastante o PC)."""
    while True:
        pasta, roteiro, molde, voz = FILA.get()
        try:
            produzir(roteiro, molde, pasta=pasta, voz=voz)
        except Exception as e:
            log.warning("vídeo %s falhou: %s", pasta.name, e)


@app.on_event("startup")
def iniciar():
    threading.Thread(target=trabalhador, daemon=True).start()
    # vídeos que estavam sendo feitos quando o programa fechou: marca como interrompidos
    for p in VIDEOS.glob("*/meta.json"):
        m = ler_json(p, {})
        if m.get("status") in ("produzindo", "na fila"):
            m.update(status="erro", erro="o programa foi fechado no meio. Clique em 'Refazer'.")
            salvar_json(p, m)


@app.get("/")
def inicio():
    return FileResponse(WEB / "painel.html")


@app.get("/api/estado")
def estado():
    return {"tem_chave": tem_chave(), "vozes": VOZES, "fila": FILA.qsize()}


# ------------------------------------------------------------------ roteiro
class PedidoRoteiro(BaseModel):
    molde: str
    modo: str = "tema"          # "tema" (a IA escreve) | "texto" (o seu texto)
    conteudo: str
    duracao: int | None = None
    palavra_cta: str = ""


@app.post("/api/roteiro")
def criar_roteiro(p: PedidoRoteiro):
    try:
        molde = M.carregar_molde(p.molde)
    except ValueError as e:
        raise HTTPException(404, str(e))
    if not p.conteudo.strip():
        raise HTTPException(400, "Escreva o tema ou o texto do vídeo.")
    if p.modo == "tema":
        if not tem_chave():
            raise HTTPException(400, "Para a IA escrever a partir de um tema, configure a chave da API do Claude "
                                     "(veja o LEIA-ME). Sem ela, use 'Meu texto'.")
        try:
            return gerar_roteiro(p.conteudo, molde, CFG.get("ia", {}), p.duracao, p.palavra_cta)
        except Exception as e:
            raise HTTPException(502, f"Não consegui escrever o roteiro: {e}")
    return roteiro_de_texto(p.conteudo, p.palavra_cta, molde.get("base", "neon"))


# ------------------------------------------------------------------ vídeos
class PedidoVideo(BaseModel):
    molde: str
    roteiro: dict
    voz: str | None = None


@app.post("/api/videos")
def criar_video(p: PedidoVideo):
    if not p.roteiro.get("cenas"):
        raise HTTPException(400, "O roteiro está vazio.")
    pasta = VIDEOS / novo_id(p.roteiro.get("titulo", "video"))
    pasta.mkdir(parents=True)
    salvar_json(pasta / "roteiro.json", p.roteiro)
    Andamento(pasta)("na fila", 0.0, status="na fila", titulo=p.roteiro.get("titulo", ""), molde=p.molde,
                     voz=p.voz or "", criado=time.time(), erro="")
    FILA.put((pasta, p.roteiro, p.molde, p.voz))
    return {"id": pasta.name}


@app.get("/api/videos")
def listar_videos():
    saida = []
    for p in sorted(VIDEOS.iterdir(), reverse=True) if VIDEOS.is_dir() else []:
        m = ler_json(p / "meta.json")
        if not m:
            continue
        m["id"] = p.name
        m["video"] = f"/midia/{p.name}/video.mp4" if (p / "video.mp4").exists() and m.get("status") == "pronto" else ""
        m["miniatura"] = f"/midia/{p.name}/miniatura.jpg" if (p / "miniatura.jpg").exists() else ""
        saida.append(m)
    return saida


@app.get("/api/videos/{vid}")
def ver_video(vid: str):
    pasta = VIDEOS / Path(vid).name
    if not (pasta / "meta.json").exists():
        raise HTTPException(404)
    return {"meta": ler_json(pasta / "meta.json"), "roteiro": ler_json(pasta / "roteiro.json")}


@app.post("/api/videos/{vid}/refazer")
def refazer(vid: str):
    pasta = VIDEOS / Path(vid).name
    m, r = ler_json(pasta / "meta.json"), ler_json(pasta / "roteiro.json")
    if not m or not r:
        raise HTTPException(404)
    Andamento(pasta)("na fila", 0.0, status="na fila", erro="")
    FILA.put((pasta, r, m.get("molde", "neon"), m.get("voz") or None))
    return {"ok": True}


@app.delete("/api/videos/{vid}")
def apagar_video(vid: str):
    pasta = VIDEOS / Path(vid).name
    if pasta.is_dir() and pasta.parent == VIDEOS:
        shutil.rmtree(pasta, ignore_errors=True)
    return {"ok": True}


# ------------------------------------------------------------------ moldes
AMOSTRA = {"titulo": "amostra", "cenas": [
    {"fala": "Isso aqui é um *molde* do Animatik.", "visual": {"tipo": "cards", "itens": [
        {"rotulo": "Roteiro", "icone": "texto"}, {"rotulo": "Voz", "icone": "microfone"}, {"rotulo": "Animação", "icone": "brilho"}]}},
]}


@app.get("/api/moldes")
def listar_moldes():
    return {"moldes": M.listar(), "tarefas": list(TAREFAS.values())}


@app.get("/api/moldes/{nome}")
def ver_molde(nome: str):
    try:
        return ler_json(MOLDES / Path(nome).name / "molde.json")
    except Exception:
        raise HTTPException(404)


@app.get("/api/moldes/{nome}/amostra.jpg")
def amostra(nome: str):
    pasta = MOLDES / Path(nome).name
    arq = pasta / "amostra.jpg"
    if not arq.exists():
        try:
            import copy
            previa(copy.deepcopy(AMOSTRA), pasta.name, arq)
        except Exception as e:
            log.warning("amostra do molde %s: %s", nome, e)
            raise HTTPException(500, "não consegui gerar a amostra")
    return FileResponse(arq, headers={"Cache-Control": "no-cache"})


@app.put("/api/moldes/{nome}")
def salvar_molde(nome: str, dados: dict):
    pasta = MOLDES / Path(nome).name
    if not (pasta / "molde.json").exists():
        raise HTTPException(404)
    atual = ler_json(pasta / "molde.json", {})
    for k in ("nome", "descricao", "marca", "formato", "topo_texto", "cursores", "voz", "velocidade", "musica",
              "volume_musica", "cores", "roteiro", "etiquetas_cursor"):
        if k in dados:
            atual[k] = dados[k] if not isinstance(dados[k], dict) else {**atual.get(k, {}), **dados[k]}
    M.salvar_molde(pasta.name, atual)
    (pasta / "amostra.jpg").unlink(missing_ok=True)
    return atual


@app.post("/api/moldes/{nome}/duplicar")
def duplicar_molde(nome: str, novo_nome: str = Form(...)):
    return {"id": M.duplicar(Path(nome).name, novo_nome)}


@app.post("/api/moldes/{nome}/avatar")
async def enviar_avatar(nome: str, arquivo: UploadFile = File(...)):
    pasta = MOLDES / Path(nome).name
    if not pasta.is_dir():
        raise HTTPException(404)
    dados = await arquivo.read()
    if len(dados) > 8_000_000:
        raise HTTPException(400, "imagem grande demais (máx. 8 MB)")
    from PIL import Image
    import io
    try:
        img = Image.open(io.BytesIO(dados)).convert("RGBA")
    except Exception:
        raise HTTPException(400, "não é uma imagem")
    img.thumbnail((800, 800))
    img.save(pasta / "avatar.png")
    (pasta / "amostra.jpg").unlink(missing_ok=True)
    return {"ok": True}


@app.delete("/api/moldes/{nome}/avatar")
def tirar_avatar(nome: str):
    (MOLDES / Path(nome).name / "avatar.png").unlink(missing_ok=True)
    return {"ok": True}


@app.delete("/api/moldes/{nome}")
def apagar_molde(nome: str):
    pasta = MOLDES / Path(nome).name
    if pasta.name in ("neon", "papel"):
        raise HTTPException(400, "Os moldes que vêm com o Animatik não podem ser apagados (dá para duplicar e mudar).")
    if pasta.is_dir() and pasta.parent == MOLDES:
        shutil.rmtree(pasta, ignore_errors=True)
    return {"ok": True}


@app.post("/api/moldes")
async def novo_molde(nome: str = Form(...), arquivos: list[UploadFile] = File(...)):
    """Cria um molde novo a partir de 1 a 3 vídeos de exemplo (a análise roda em segundo plano)."""
    if not tem_chave():
        raise HTTPException(400, "Para ler o estilo dos exemplos, configure a chave da API do Claude (veja o LEIA-ME). "
                                 "Sem ela, duplique um molde pronto e ajuste as cores.")
    if not 1 <= len(arquivos) <= 3:
        raise HTTPException(400, "Mande de 1 a 3 vídeos de exemplo.")
    tmp = Path(tempfile.mkdtemp(prefix="exemplos_"))
    salvos = []
    for a in arquivos:
        destino = tmp / Path(a.filename or "exemplo.mp4").name
        with open(destino, "wb") as f:
            while bloco := await a.read(1 << 20):
                f.write(bloco)
        salvos.append(destino)
    tid = secrets.token_hex(4)
    TAREFAS[tid] = {"id": tid, "nome": nome, "status": "analisando", "erro": ""}

    def tarefa():
        try:
            slug = M.criar_de_exemplos(nome, salvos, CFG.get("ia", {}))
            TAREFAS[tid].update(status="pronto", molde=slug)
        except Exception as e:
            log.warning("molde %s: %s", nome, e)
            TAREFAS[tid].update(status="erro", erro=str(e)[:400])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    threading.Thread(target=tarefa, daemon=True).start()
    return TAREFAS[tid]
