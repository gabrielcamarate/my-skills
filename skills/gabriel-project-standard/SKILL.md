---
name: gabriel-project-standard
description: "Levar um projeto ao padrão de projeto de Gabriel (fluxo Akita): AGENTS.md curto, permissões, fast-check, nuvem, CI barato no PR e pesado pós-merge, staging→main com gate, versão na promoção e revisor de domínio."
---

# Padrão de projeto

Fonte da verdade: `Gabriel-OS/references/padrao-de-projeto.md` e `decisions/log.md`. Exemplos vivos e provados: Xlondz, Rakmma, Maison Éclat. Os modelos em `references/templates/` (`claude/` = `.claude/`, `github/` = `.github/`) vêm do Maison (Node/pnpm); adapte, não copie às cegas.

1. **Levante antes de mudar.** Stack, comandos reais de lint/typecheck/teste/build, serviços externos (que viram stub ou variável falsa), branch padrão, se existe `staging`, deploy atual, dono do repositório. Repo pessoal privado não aceita proteção de branch: peça a Gabriel para movê-lo para uma org da enterprise. Uma issue para a adoção; trabalhe numa branch.
2. **Instruções.** `AGENTS.md` com menos de 700 palavras a partir de `references/AGENTS.template.md`: o que é o projeto, fluxo em passos com os comandos reais, invariantes de domínio, autoridade, docs sob demanda. `CLAUDE.md` é só `@AGENTS.md`. Texto antigo inteiro vai para `docs/development/agent-reference.md`, sem perda. `ARCHITECTURE.md` a partir de `references/ARCHITECTURE.template.md`, conferido no código.
3. **Permissões.** `.claude/settings.json` do modelo: pode (dev, git de tarefa, `gh pr create/merge --squash`, `git worktree remove`), pergunta (produção, SSH, banco remoto, deploy manual), nunca (force, `reset --hard`, `rm -rf`, `--force` em worktree, `gh pr merge --admin`, segredos). Troque `__PROJECT__` e ajuste aos comandos do projeto.
4. **Núcleo rápido e nuvem.** `scripts/fast-check.sh` (o `bin/ci` do Akita: lint, typecheck, unitários, build, sem credencial), `scripts/cloud-setup.sh` (troque `__GIT_NAME__`/`__GIT_NOREPLY_EMAIL__` pela identidade noreply do dono), `scripts/ensure-node.sh` com `test-ensure-node.sh`. Preencha `__DUMMY_ENV__` só com valores falsos e públicos. Prove num ambiente limpo (`env -i`, HOME vazio).
5. **Gates obrigatórios (não apague passos do CI):** `scripts/__PROJECT__-workflow.py` fornece `doctor` e `staging-ready --expected-sha <sha>` (a pesada `staging-quality.yml` precisa ter `success` no push com `head_sha` igual à ponta da `staging`); `scripts/check-pr-scope.py` exige branch `<tipo>/<N>-...` e `Refs #N`. Sem eles o gate falha aberto. `__DUMMY_ENV__` vazio deixa o build ler `.env.local` real: preencha ou force no script.
6. **CI modo Akita.** `pr.yml`: check obrigatório barato no PR para `staging` (~1 min: segredos, escopo, versão, verificadores); PR para `main` roda o completo e só aceita origem `staging` do próprio repo; gatilho com `edited`; nenhum `if` no job obrigatório. `staging-quality.yml`: suíte pesada no push da `staging`, abre/fecha a issue "staging vermelha: <sha>". Sem merge queue.
7. **Parar a linha.** O início de tarefa e o passo antes de cada merge conferem a pesada na ponta da `staging`; vermelha, corrige primeiro ou para.
8. **Entrega.** Crie `staging` a partir da branch padrão. Rulesets via `gh api` (`references/rulesets.md`): `staging` e `main` só por PR, sem force nem deleção, check obrigatório do GitHub Actions, **sem strict nos dois**; `staging` só squash; `main` squash e merge commit. O merge da promoção (`--merge`) fica em "pergunta" no settings. Promoção só com OK de Gabriel no chat, merge commit com `--match-head-commit`, gate exigindo a pesada verde no SHA da `staging`. Versão cortada na promoção (`release.mjs` ou equivalente); PRs com `Refs #N`, nunca `Closes`.
9. **Revisor de domínio** (opcional, só se houver invariantes que um revisor genérico não conhece): `references/reviewer.template.md`, ~120 palavras, Claude `claude-opus-5-5`/`high` e Codex com modelo fixo. Sem "specialist".

**Aceite:** todos os itens do padrão marcados; um PR pequeno de prova chega à `staging` em poucos minutos; pesada verde na ponta; tabela de estado do `padrao-de-projeto.md` atualizada.
**Fica com Gabriel:** segredos e variáveis de ambiente, ambientes de nuvem (Claude e Codex), mover o repositório para org, criar serviços pagos.
**Não faça:** orquestração, watchers, ferramentas do my-tools congelado, mudança de produto junto com a adoção.
