# Animatik: vídeos animados com IA, no seu estilo

Você escolhe um **estilo (molde)**, diz **sobre o que é o vídeo**, revisa o roteiro e o Animatik faz o resto:

1. **Roteiro**: a IA escreve a partir de um tema (com a chave da API do Claude), ou você cola o seu texto.
   Cada frase vira uma cena. Palavras entre `*asteriscos*` ficam destacadas na tela.
2. **Narração** com voz de IA em português (grátis), e o tempo de cada palavra para o texto aparecer junto com a fala.
3. **Animação** de cada cena (motion design: texto entrando, cards, etapas, número contando, gráfico, lista, avatar...).
4. **Efeitos sonoros e música** feitos pelo próprio programa (sem direitos autorais), música abaixando quando tem fala,
   volume no padrão do TikTok/Reels.
5. Vídeo **vertical 1080x1920, 30 fps**, pronto para postar, com a legenda do post.

É um programa separado do Tesourex. Os dois podem ficar ligados ao mesmo tempo (o Tesourex usa a porta 8000,
o Animatik a 8100).

## Instalar e ligar (Windows)

1. Descompacte o zip num disco com espaço (ex.: `D:\Animatik`).
2. Dê dois cliques em **INICIAR.bat**.

Na primeira vez ele instala o que faltar (Python, FFmpeg, bibliotecas e o "navegador gravador", uns 150 MB, que fica
dentro da pasta `navegador`). Se pedir para fechar e abrir de novo, é só fazer isso.

Ele pergunta (uma vez só) a **chave da API do Claude**. É opcional:
- **com a chave**: a IA escreve o roteiro a partir de um tema e lê o estilo dos seus vídeos de exemplo;
- **sem a chave**: você escreve o texto e o Animatik monta o vídeo do mesmo jeito.

A chave fica só no seu PC (arquivo `chave_api.txt`). Não mande para ninguém, nem para o Claude no chat.
Para trocar ou colocar depois: apague `chave_api.txt` e `.sem_chave` e abra o INICIAR.bat de novo.
A chave se cria em console.anthropic.com (é paga por uso; escrever um roteiro custa poucos centavos).

O painel abre sozinho em **http://localhost:8100**. Para desligar, feche a janela "Animatik (nao feche)".

## O painel

- **Criar**: escolha o molde, escreva o tema (ou o seu texto), a duração, a palavra para comentarem e a voz.
  Clique em **Escrever roteiro**, revise as cenas (dá para mudar a fala, o tipo de visual, a ordem) e
  clique em **Produzir vídeo**.
- **Vídeos**: o andamento de cada vídeo e os prontos, com **Baixar**, **Copiar legenda**, **Refazer** e **Apagar**.
  Um vídeo de 40 s leva de 1 a 4 minutos (depende do PC).
- **Moldes**: os estilos.
  - **Novo molde a partir de exemplos**: mande de 1 a 3 vídeos no estilo que você quer. A IA olha os vídeos e monta
    o molde (cores, tipo de animação, voz, música, jeito do roteiro, gancho e chamada). Precisa da chave da API.
  - Clique num molde para **ajustar**: nome, marca do canto, cores, formato (vertical ou "tela filmada", que mostra a
    animação num monitor em cima da mesa), voz, velocidade, música, faixa de texto em cima, cursores "editando",
    tom do roteiro, gancho, chamada final e **avatar** (mande uma foto ou desenho PNG seu).
  - **Duplicar** para criar variações sem mexer no original.

## Moldes que já vêm prontos

- **Neon (tela de sistema)**: fundo escuro, verde neon com brilho, cantinhos, "REC", cards e texto de terminal.
- **Papel (caneta azul + avatar)**: fundo creme, texto preto com a palavra-chave em azul itálico, avatar desenhado
  e cursores coloridos "editando".

## Tipos de cena

| tipo | o que mostra |
|---|---|
| titulo | palavra gigante (pode ser riscada, para negar algo) |
| comando | caixa de pedido sendo digitada |
| cards | 2 a 4 cartões com ícone |
| fluxo | etapas ligadas por linha (A → B → C) |
| riscado | "em vez de": o antes riscado e o depois aparecendo |
| numero | número grande contando, com anel |
| grafico | linha subindo com pico |
| lista | itens sendo marcados |
| icone | ícone grande pulsando |
| avatar | o boneco do apresentador com balão |
| cta | chamada final ("Comenta PALAVRA") |

Escrevendo o seu texto (sem a chave), o Animatik escolhe sozinho: frase com "em vez de" vira riscado, frase com
número vira número contando, frase com "→" vira etapas, e as outras alternam entre os demais tipos.
Termine com "Comenta *PALAVRA*." para ganhar a chamada final.

## Sem painel

```
python main.py criar meu_roteiro.txt --molde papel
```

## Problemas

- **"não consegui gerar a narração"**: a voz grátis precisa de internet.
- **Vídeo demorando**: é normal levar alguns minutos; cada quadro da animação é desenhado e gravado.
- Qualquer outro erro: tire um print da janela "Animatik" e mande para o Claude.
