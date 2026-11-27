---
name: navegador-e-prints
description: Abre páginas no navegador disponível no runtime (OpenBot, Claude Code, Devin ou outro), confere o que aparece e tira prints da tela para mostrar o resultado. Use quando precisar ver uma página, conferir uma interface ou gerar evidência visual de uma mudança.
example-prompt: Abra a página de teste, confira a mensagem de erro e tire um print da tela.
---

# Navegador e prints

Objetivo: ver o que a página mostra de verdade e entregar um print com uma linha descrevendo o que aparece.

Esta skill descreve capacidades, não ferramentas. Use a ferramenta que o seu runtime oferece para cada capacidade (veja a tabela abaixo). Se nenhuma estiver disponível, diga isso e não invente a verificação.

## Capacidades

| Capacidade | OpenBot | Claude Code | Devin |
| --- | --- | --- | --- |
| Listar abas | `openbot_browser.list_tabs` | Playwright MCP: `browser_tabs` | Navegador nativo (ferramenta `computer`) |
| Abrir URL | `openbot_browser.open` | Playwright MCP: `browser_navigate` | Navegador nativo (ferramenta `computer`) |
| Ler a página | snapshot retornado / `openbot_browser.run_script` | Playwright MCP: `browser_snapshot` | DOM anotado retornado pela ferramenta `computer` |
| Tirar print | Computer Use: `get_window_state` com `include_screenshot` true | Playwright MCP: `browser_take_screenshot` | Screenshot retornado pela ferramenta `computer` |

Outros runtimes: use qualquer MCP de navegador (Playwright MCP, Chrome DevTools MCP) ou o navegador nativo do agente. Veja `RUNTIMES.md` na raiz do repositório Mires.

## Fluxo
1. Liste as abas abertas e reaproveite a aba do site certo, se houver.
2. Abra a URL. Leia o snapshot ou o DOM da página antes de agir.
3. Tire o print da janela ou da página. Se a captura não estiver disponível, diga isso e descreva o que viu no snapshot.
4. Entregue o print com uma linha: o que aparece e em qual URL.

## Limites
- Não preencha formulários com dados reais, não envie nada e não faça login sem aprovação do dono.
- Não mostre senhas, tokens ou cookies, nem os coloque em URLs.
- Se a página pedir login, pare e peça ao dono para entrar.
- Não diga que algo foi verificado se você não viu na página.

## Verificação
A tarefa está pronta quando o print e a linha de descrição foram entregues, com a URL confirmada.
