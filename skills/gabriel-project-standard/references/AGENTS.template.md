# __PROJECT_NAME__

<Uma ou duas frases: o que é, para quem, stack principal.> Leia `README.md` e `ARCHITECTURE.md` antes de mudar estrutura.

## Fluxo de uma issue

1. Uma issue por vez. Parta de `origin/staging`: `git -C <repo> worktree add ../<repo>-<issue> -b <type>/<issue>-<desc> origin/staging`. Antes, confira a suíte pesada na ponta da `staging`; vermelha (ou issue "staging vermelha" aberta), corrija isso primeiro ou pare e reporte.
2. Teste que falha primeiro (bug vira teste de regressão), depois a implementação.
3. `./scripts/fast-check.sh` verde antes do push (local ou nuvem). Na nuvem, `./scripts/cloud-setup.sh` prepara o ambiente.
4. Notas em `## Unreleased` do CHANGELOG; não mude a versão (ela é cortada na promoção).
5. PR para `staging`: título em inglês Conventional, corpo em pt-BR terminando com `Refs #N` (nunca `Closes`). Mudança sensível (<listar: auth, pagamento, segredos, CI/gates, migrations, permissões e instruções de agente>) passa por revisão independente antes do merge.
6. Check barato verde: `gh pr merge N --squash`. Confira de novo a pesada da `staging` antes do merge.
7. Promoção `staging → main` só com OK de Gabriel no chat: PR de release corta a versão, gate verde, `gh pr merge N --merge --match-head-commit <head avaliado>`.
8. Limpeza: `git -C <repo> worktree remove <pasta>` (sem `--force`); se recusar, pare e reporte.

Mesma falha 3 vezes ou correção da correção: pare e chame Gabriel.

## Invariantes do domínio

- <regra estável, com como é verificada (teste, script, CI)>

## Autoridade

O agente faz, sem perguntar: branch, commit, push de branch de tarefa, PR, merge em `staging`, limpeza da própria tarefa. Pergunta antes: promoção para `main`, produção, banco remoto, segredos, gasto. Nunca: force push, `reset --hard`, `rm -rf`, `gh pr merge --admin`. As listas exatas estão em `.claude/settings.json`.

## Docs sob demanda

| Quando | Leia |
|---|---|
| Mudar estrutura | `ARCHITECTURE.md` |
| Release e promoção | `docs/operations/releases.md` |
| Texto completo das regras antigas | `docs/development/agent-reference.md` |
