# Fazedor de Vídeo: instruções para o Claude

O dono deste projeto pede vídeos curtos (Reels/TikTok, vertical) pelo chat, muitas vezes pelo celular.
Ele não programa. Fale com ele em português simples, sem termos técnicos. Ele quer **o MP4 pronto**, não código.

## O pedido típico

"Faz um vídeo de 30 segundos sobre X" (às vezes com estilo, voz ou exemplos). Fluxo:

1. **Roteiro**: escreva a história (storytelling curto, que faça sentido para quem não conhece o assunto).
   - Estrutura que funciona: gancho/problema concreto → apresenta o produto/assunto → como funciona (2 a 3 passos)
     → resultado (antes e depois) → chamada ("Comenta PALAVRA").
   - 6 a 9 cenas, uma frase curta por cena (4 a 14 palavras). ~2,4 palavras por segundo de vídeo.
   - Marque 1 ou 2 palavras-chave por cena com `*asteriscos*` (ficam destacadas).
   - Escreva números por extenso quando a fala for diferente da escrita.
   - Tom: simples, caloroso, uma pitada de humor. Nada de linguagem de vendedor.
2. **Visual de cada cena**: para histórias/produtos, **desenhe** a cena (`"tipo": "ilustracao"` com um SVG feito
   para aquele tema). Misture com 1 ou 2 cenas de tipos prontos (riscado, numero, fluxo, cta) para variar.
3. **Produzir**: `python main.py criar caminho/roteiro.json --molde rustico`
4. **Conferir**: tire 1 quadro por cena (`ffmpeg -i video.mp4 -vf "fps=1/1.6,scale=180:-2,tile=10x2" -frames:v 1 tira.jpg`)
   e olhe: desenho cortado, texto encavalado, cena vazia. Corrija e produza de novo.
5. **Entregar**: mande o MP4 (SendUserFile), com a legenda do post pronta para colar, e diga em 2 ou 3 linhas o que
   tem em cada parte. Guarde o roteiro em `pedidos/AAAA-MM-DD-tema/` (o .py que gera o JSON + o JSON) e faça commit.

## Preparar a máquina (sessão nova na nuvem)

```
pip install -q edge-tts playwright fastapi uvicorn python-multipart pyyaml numpy pillow
export ANIMATIK_CHROMIUM=/opt/pw-browsers/chromium   # Chromium que já vem na máquina (não rode "playwright install")
```
- FFmpeg já vem instalado. A voz grátis (edge-tts) precisa do host `speech.platform.bing.com` liberado na rede do
  ambiente (já foi liberado no ambiente Default). As fontes ficam em `web/fontes/` (não precisa de internet).
- Um vídeo de 30 s leva ~3 minutos para gravar.

## Formato do roteiro (JSON)

```json
{"titulo": "...", "legenda_post": "texto do post com 3 a 6 hashtags",
 "cenas": [{"fala": "Imagina colher um *milharal* inteiro... na mão.", "visual": {"tipo": "ilustracao", "svg": "<svg ...>"}, "pausa": 0.35}]}
```
`pausa` (opcional) = silêncio depois da fala (padrão 0.24 s; 0.42 depois de "?" ou "...").

### Tipos de visual prontos
titulo (texto, riscar, sub) · comando (texto, titulo, destaque[]) · cards (itens[{rotulo, icone, sub}]) ·
fluxo (itens) · riscado (rotulo, antes, depois, icone, icone_depois) · numero (valor, sufixo, porcento, rotulo) ·
grafico (pontos[], titulo, rotulo) · lista (itens) · icone (icone, rotulo) · avatar (texto, etiqueta) · cta (palavra, rotulo, logo).
**Marca/empresa**: use `{"tipo": "marca", "logo": "<svg da logo>", "sub": "frase curta"}` e `cta` com `"logo"`. A logo fica FORA
do desenho, então nenhum estilo muda as cores dela (ex.: `logo_claroflex()` em `pedidos/2026-11-24-claroflex/roteiro.py`).
Sem som de "whoosh" entre cenas (ele pediu áudio fluido); só volta se o molde tiver `"som_transicao": true`.
Ícones: ver `web/icones.js`.

### Ilustração (o diferencial)
O SVG é desenhado por você para cada cena (veja `exemplos/colhedeira_milho.py`: funções reutilizáveis de pé de milho,
roceiro, colhedeira, sol, chão). Use `viewBox` justo no conteúdo (o desenho ocupa a largura toda).
Traço: `stroke="#3a2716" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"`; cores chapadas de terra.
O motor aplica sozinho o "tremido de lápis". Animação por atributos nos elementos:

| atributo | efeito |
|---|---|
| `data-entra="esq|dir|cima|baixo|zoom|pop|cai|fade|desenha"` + `data-t` (início, s) + `data-d` (duração) | entrada |
| `data-mover="dx,dy"` (+ `data-mover-d` = em quantos segundos) | anda durante a cena |
| `data-girar="graus/s"` | gira (rodas, engrenagens) |
| `data-balanca="graus"` + `data-fase` | balança (plantas, placas) |
| `data-pulsa="0.04"` | pulsa |
| `data-tomba="-82"` + `data-tomba-t="1.2"` | cai deitado nessa hora |
| `data-origem="50% 100%"` | ponto de giro (padrão: centro) |
| `data-som="motor|graos|pop|impacto|transicao|risco|ding|check"` + `data-som-d` | efeito sonoro nessa hora |

Texto dentro do desenho: `<text font-family="Caveat" ... stroke="none">`.

## Moldes (estilos)
- `rustico`: papel kraft, lápis, violão. Para histórias e produtos (padrão).
- `claroflex-3d`: vídeos da Claroflex (sogro): 3D, destaque no vermelho da logo (#e3262f), voz 1 Antônio. Ele pediu: não dizer
  "enferruja"; a cortina desliza e abre na lateral em L; final = só a logo + "Faça seu orçamento no link da bio" (sem "Comenta").
  Dar ênfase: "a Claroflex, uma empresa europeia, desenvolveu o sistema" (sem citar a Espanha); o vidro "desliza no trilho inferior" (nunca "no chão").
- `neon`, `neon-tela` (tela filmada), `papel` (caneta azul + avatar).
- **16 estilos de animação** (`est-*`, base `estilo` + `acabamento`): o MESMO desenho da ilustração muda de cara.
  Se ele pedir "no estilo X", use o molde correspondente:
  `est-chapado` cartoon chapado · `est-pixel` pixel art · `est-caderno` rabisco de caderno · `est-recorte` recorte de papel ·
  `est-lousa` lousa branca · `est-neon80` neon anos 80 · `est-minimal` minimalista com contador (molde.contador_final) ·
  `est-sombras` teatro de sombras · `est-massinha` massinha/stop motion · `est-cordel` xilogravura de cordel ·
  `est-planta` planta técnica · `est-lowpoly` low poly 3D · `est-filme` filme mudo · `est-quadrinhos` história em quadrinhos
  (visual.onomatopeia muda o "VRUUM!" da cena) · `est-terminal` terminal de código · `est-3d` 3D de verdade.
  - Os estilos de traço (caderno, lousa, planta) desenham sozinhos tudo que não tem `data-entra`; os de silhueta
    (sombras, minimal) usam só o contorno: desenhe formas bem reconhecíveis pela silhueta.
  - Desenhe com cores chapadas e contorno normal: cada estilo troca cor/traço/filtro sozinho (`web/estilos.js` e `web/estilos.css`).
  - Mostruário (o mesmo foguete nos 16): `python ferramentas/mostruario.py [est-...]` → `saida/mostruario/`.
Molde = `moldes/<nome>/molde.json` (cores, fontes, voz, velocidade, tom_voz, musica: pulso|lofi|violao).
Se ele mandar vídeos de exemplo: olhe quadros (`ffmpeg ... tile`), crie um molde novo copiando o mais parecido e
ajustando cores/fontes/música/tom do roteiro.

## Vozes
`animatik/voz.py` (VOZES). Padrão: pt-BR-AntonioNeural. **Use só as vozes pt-BR (1, 2, 3).** As "Multilingual" (4 a 10)
adivinham o idioma de cada frase e já trocaram para espanhol no meio de um vídeo ("Claroflex", "sistema europeu").
Amostra: gere 1 frase e mande antes de um vídeo grande, se ele pedir.

## Programa para o PC dele
O mesmo código roda no Windows com painel (INICIAR.bat → http://localhost:8100). Ele usa sem chave de API
(escreve o texto, o programa monta). Se mudar algo que vale para o PC também, avise que dá para gerar um zip novo.
