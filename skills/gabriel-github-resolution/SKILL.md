---
name: gabriel-github-resolution
description: "Resolver uma issue aprovada de ponta a ponta: um ticket por vez, teste antes do fix, núcleo rápido verde, PR limpo e entrega pelo fluxo do projeto."
---

# Resolução de issue

Um ticket aprovado por vez. Os comandos vêm do fluxo no `AGENTS.md` do projeto. Exemplo vivo: Xlondz.

1. Comece pelo comando do projeto (Xlondz: `./scripts/xlondz start`; `--resume` para continuar). Em ambiente novo ou na nuvem, rode o setup (Xlondz: `./scripts/cloud-setup.sh`). A branch segue `<type>/<issue>-<desc>`, nunca `claude/` ou `codex/`.
2. Defina o oráculo (o que prova que está pronto). Escreva o teste de regressão e veja-o **falhar** antes do fix. Slop é defeito: nada de abstração especulativa, refactor de passagem ou teste enfraquecido.
3. Rode o núcleo rápido até ficar verde (Xlondz: `./scripts/fast-check.sh web|manager`). **Disjuntor:** a mesma falha 3 vezes ou a correção da correção → pare e chame Gabriel com o que sabe. Source: xlondz#463.
4. Versão, CHANGELOG, README e runbook afetado no mesmo PR (Xlondz: `./scripts/xlondz release cut --bump …` e `release check --base origin/main`).
5. PR em pt-BR com `Refs #N`, evidência no corpo e sem atribuição ao Claude. Nunca `Closes`/`Fixes`/`Resolves` no corpo nem no título: a issue só fecha depois do aceite, e o CI recusa. Antes de criar, `grep -iE '(close|fix|resolve)[sd]? #' <corpo>` deve vir vazio. Source: xlondz#523, xlondz#532. **Na nuvem, a linha de chegada é esta: PR com o núcleo verde. Abra o PR e encerre a sessão; não fique acompanhando CI nem agende checagens, porque revisão e merge acontecem localmente.** Source: xlondz#519.
6. Mais de 3 tickets com código na mesma sessão: audite o intervalo composto ([composição](references/composition.md)) antes do push final.
7. De ponta a ponta, localmente:
   1. Gate do projeto (Xlondz: `./scripts/xlondz integration-ready --pr N`, com as dependências do `web/` instaladas).
   2. Squash com mensagem própria: `gh pr merge N --squash --subject "<type>(<scope>): <resumo> (#PR)" --body "<o que mudou>. Refs #M"`. Nunca a lista de commits nem trailers. Source: xlondz#517.
   3. CI da main, publicação e deploy pelo workflow.
   4. Smokes, fechamento (Xlondz: `./scripts/xlondz complete`) e limpeza de branch e worktree.
8. Se o deploy falhar: confira a produção, reconcilie o estado real e não reenvie às cegas. Registre na issue. Source: xlondz#520.

Comandos: `git -C <worktree> ...` e `gh <comando> ... --repo <owner/repo>` (o `--repo` no fim: `gh --repo X pr ...` não casa com as permissões liberadas e o modo automático bloqueia), nunca `cd <worktree> && git ...`. Um comando por chamada, sem heredoc, `$(...)` ou pipes; corpo do PR em arquivo escrito pela ferramenta de edição e `gh pr create --body-file`. Source: maison-eclet 16/10, my-finances #127 e rakmma #881, 21/10/2026.

Limpeza: `git -C <repo> worktree remove <pasta>` sem `--force`; se recusar, pare e reporte. Nunca `rm -rf`. Source: rakmma, sessões de 16/10/2026.

Toda espera tem prazo (`timeout` ou contador); nunca laço `until` sem limite. Para CI: `timeout 1800 gh pr checks N --watch --fail-fast`. Source: maison-eclet, laço preso por 1 h em 16/10/2026.
