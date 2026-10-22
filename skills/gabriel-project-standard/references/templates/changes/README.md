# Notas de mudança

Cada PR de tarefa cria **um** arquivo `changes/<N>-<slug>.md`, com `N` = número da
issue da branch, e não edita o `CHANGELOG.md`. Assim PRs paralelos não conflitam.

```md
### Corrigido
- Frase curta em português sobre o que muda para quem usa ou opera (#N).
  Linhas de continuação ficam indentadas.
```

- Linhas aceitas: `- item`, continuação indentada logo depois de um item, linha em
  branco e `### <categoria>`.
- Categorias: `Adicionado`, `Alterado`, `Corrigido`, `Removido`, `Segurança`. O
  cabeçalho é opcional; nota sem categoria vai para o topo da versão.
- `node scripts/release.mjs check` valida nome e conteúdo; o check de escopo do PR exige a nota
  da própria issue e recusa alteração no `CHANGELOG.md` ou em nota alheia.
- O corte de versão (`node scripts/release.mjs prepare --bump ...`, no PR que muda a
  versão do `package.json`) junta as notas na nova seção,
  agrupadas por categoria e em ordem de issue, e apaga os arquivos no mesmo commit.

Este `README.md` não é nota e permanece.

**Migração única:** se o `CHANGELOG.md` ainda tem itens em `## Unreleased`, o primeiro
PR de tarefa depois da adoção move esse conteúdo para `changes/0-unreleased-legacy.md`
(no formato acima), apaga a seção `## Unreleased` e não muda mais nada no
`CHANGELOG.md`. O check de escopo só aceita isso enquanto a ponta da `staging` ainda
tem `## Unreleased` com itens.
