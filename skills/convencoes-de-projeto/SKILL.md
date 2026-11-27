---
name: convencoes-de-projeto
description: "Antes de implementar qualquer mudança em um projeto, lê as convenções dele (AGENTS.md, README, guias de contribuição, configs de lint, formatação e testes, CI) e segue o padrão existente. Use no início de toda tarefa de código em repositório, em qualquer stack."
---

# Convenções de projeto antes de codar

## Objetivo
Antes de escrever código em um projeto, descubra e siga as convenções dele. As convenções do projeto têm prioridade sobre qualquer padrão de stack do agente. Esses padrões valem só como fallback quando o projeto não define os seus.

## Procedimento

1. **Localize a raiz do projeto.** Confirme o caminho com o dono se ele não foi informado. Trabalhe só dentro do repositório indicado.
   - Pitfall: editar fora da raiz correta mistura convenções de projetos diferentes. Confirme a raiz antes de qualquer escrita.

2. **Leia os documentos de convenção, nesta ordem:** `AGENTS.md`, `README.md`, `CONTRIBUTING.md` (ou guia equivalente), `Makefile`, `.github/` (workflows de CI e templates).
   - Use `ls -la` na raiz e `head -c 4000` nos arquivos encontrados, para limitar a saída.
   - Pitfall: ler só o README perde regras de contribuição e de CI. Leia o conjunto.

3. **Leia as configs de ferramentas.** Procure por: `.editorconfig`, `biome.json(c)`, `.eslintrc*`, `eslint.config.*`, `.prettierrc*`, `checkstyle*`, `spotless`, `pmd*`, `pom.xml`, `build.gradle*`, `pyproject.toml`, `setup.cfg`, `ruff.toml`, `tsconfig.json`, `package.json`.
   - Extraia do `package.json` ou do `Makefile` os scripts oficiais de lint, typecheck, test e build.
   - Pitfall: inventar comandos gera falso sucesso. Use só os scripts que o projeto declara.

4. **Identifique a stack real.** Leia o manifesto de dependências (`package.json`, `pom.xml`, `pyproject.toml`, etc.). Não assuma a stack padrão do agente.
   - Pitfall: o projeto pode usar outra linguagem ou runtime. Assumir a stack errada faz o código não compilar ou não passar no lint.

5. **Observe o padrão do código existente.** Antes de criar um arquivo, veja vizinhos parecidos: nomes, estrutura de pastas, alias de import, tratamento de erro, testes.
   - Pitfall: seguir a documentação e ignorar o código vivo cria divergência. Quando os dois conflitam, sinalize ao dono.

6. **Só então implemente.** Faça mudanças pequenas e revisáveis.

7. **Verifique com os comandos do projeto.** Rode lint, typecheck, testes e build que existem. Se algum não puder rodar, diga qual e por quê.
   - Pitfall: relatar sucesso sem rodar é o erro mais grave. Registre o que foi verificado e o que não foi.

## Regras de decisão
- Se a convenção do projeto contradiz a stack padrão, siga o projeto.
- Se o projeto não define uma regra, use o fallback do agente e registre a escolha.
- Antes de adicionar dependência, verifique se o projeto já tem uma equivalente. Prefira pacotes oficiais do ecossistema em uso.
- Não leia arquivos de segredo (`.env`, chaves, credenciais). Não os copie para saídas.

## Formato do resultado
Ao terminar, informe em texto curto:
- Convenções encontradas que guiaram a mudança.
- Arquivos criados ou alterados.
- Comandos executados e resultado de cada um.
- O que não foi verificado e o motivo.

## Resumo inicial (quando pedido só para ler)
Resuma em poucas linhas: stack, ferramentas de lint e formato, estilo (indentação, aspas, largura, imports), arquitetura, comandos oficiais e pontos ainda não lidos. Não altere arquivos nessa fase.
