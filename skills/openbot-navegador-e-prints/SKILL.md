---
name: openbot-navegador-e-prints
description: Abre páginas no navegador do OpenBot, confere o que aparece e tira prints da tela para mostrar o resultado. Use quando precisar ver uma página, conferir uma interface ou gerar evidência visual de uma mudança.
example-prompt: Abra a página de teste, confira a mensagem de erro e tire um print da tela.
---

# Navegador e prints

Objetivo: ver o que a página mostra de verdade e entregar um print com uma linha descrevendo o que aparece.

## Fluxo
1. Use `openbot_browser.list_tabs` para ver as abas abertas. Reaproveite a aba do site certo.
2. Abra a URL com `openbot_browser.open`, ou navegue com `openbot_browser.run_script`. Leia o snapshot retornado antes de agir.
3. Para o print, capture a janela do navegador com o Computer Use (`get_window_state` com `include_screenshot` true), escolhendo a janela pelo título. Se a captura não estiver disponível, diga isso e descreva o que viu no snapshot.
4. Entregue o print com uma linha: o que aparece e em qual URL.

## Limites
- Não preencha formulários com dados reais, não envie nada e não faça login sem aprovação do dono.
- Não mostre senhas, tokens ou cookies, nem os coloque em URLs.
- Se a página pedir login, pare e peça ao dono para entrar.
- Não diga que algo foi verificado se você não viu na página.

## Verificação
A tarefa está pronta quando o print e a linha de descrição foram entregues, com a URL confirmada.
