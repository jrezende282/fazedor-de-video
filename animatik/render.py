"""
Grava a animação em vídeo: abre a página web/render.html num navegador invisível, desenha cada quadro
(desenhar(t)) e tira uma foto. As fotos viram o vídeo no FFmpeg.
"""
import json
import subprocess
import time
from pathlib import Path

from .util import WEB, log


def _navegador(p):
    import os
    caminho = os.environ.get("ANIMATIK_CHROMIUM")  # navegador já instalado em outro lugar (opcional)
    if caminho:
        return p.chromium.launch(executable_path=caminho)
    try:
        return p.chromium.launch()
    except Exception:
        # navegador do Playwright ainda não instalado: instala e tenta de novo
        import sys
        log.info("instalando o navegador do gravador (só na primeira vez)...")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=False)
        return p.chromium.launch()


def renderizar(dados: dict, destino: Path, progresso=None) -> dict:
    """Grava o vídeo (sem som) e devolve {"sons": [...]} com os efeitos que a animação pediu."""
    from playwright.sync_api import sync_playwright
    fps = int(dados.get("fps", 30))
    dur = float(dados["duracao"])
    total = int(round(dur * fps))
    with sync_playwright() as p:
        nav = _navegador(p)
        pag = nav.new_page(viewport={"width": dados["largura"], "height": dados["altura"]}, device_scale_factor=1)
        pag.add_init_script(f"window.DADOS = {json.dumps(dados, ensure_ascii=False)};")
        erros = []
        pag.on("pageerror", lambda e: erros.append(str(e)))
        pag.goto((WEB / "render.html").as_uri())
        pag.wait_for_function("window.PRONTO !== undefined")
        pag.evaluate("window.PRONTO")
        if erros:
            raise RuntimeError("erro na animação: " + erros[0])
        sons = pag.evaluate("window.SONS")
        cdp = pag.context.new_cdp_session(pag)
        ff = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(fps), str(destino)],
            stdin=subprocess.PIPE)
        import base64
        inicio = time.time()
        try:
            for i in range(total):
                pag.evaluate(f"desenhar({i / fps:.5f})")
                foto = cdp.send("Page.captureScreenshot", {"format": "jpeg", "quality": 93, "optimizeForSpeed": True})
                ff.stdin.write(base64.b64decode(foto["data"]))
                if progresso and i % 15 == 0:
                    progresso(i / total, time.time() - inicio)
        finally:
            ff.stdin.close()
            ff.wait()
            nav.close()
        if erros:
            raise RuntimeError("erro na animação: " + erros[0])
        if ff.returncode != 0:
            raise RuntimeError("o FFmpeg não conseguiu gravar o vídeo")
    return {"sons": sons}


def foto(dados: dict, t: float, destino: Path) -> Path:
    """Uma imagem de um instante (para a miniatura e para conferir o visual)."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        nav = _navegador(p)
        pag = nav.new_page(viewport={"width": dados["largura"], "height": dados["altura"]})
        pag.add_init_script(f"window.DADOS = {json.dumps(dados, ensure_ascii=False)};")
        pag.goto((WEB / "render.html").as_uri())
        pag.wait_for_function("window.PRONTO !== undefined")
        pag.evaluate("window.PRONTO")
        pag.evaluate(f"desenhar({t})")
        pag.screenshot(path=str(destino), type="jpeg", quality=88)
        nav.close()
    return destino
