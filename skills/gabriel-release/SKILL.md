---
name: gabriel-release
description: "Preparar uma release versionada e executar somente a publicação autorizada, vinculando versão, candidato, CI e artefatos."
---

# Release

## Entrada
Escopo e estratégia de release do projeto, candidato integrado e autoridade atual. “Preparar” termina com um candidato revisável. Publicar exige autorização que cubra versão, destino e ação; reaproveite a que já existe.

1. Identifique branch de release, último marco publicado, candidato, árvore local e pendências. Reconcile issues e changelog com o código. Uma release não deve absorver tickets ainda não aprovados.
2. Escolha a versão pela política real e impacto: correção, adição compatível ou quebra de contrato. Confira todas as fontes de versão e metadados de pacote. Não deduza compatibilidade apenas do título de PR.
3. Verifique auditorias e gates exigidos. Para lote composto, confirme a evidência de integração. Uma alteração de versão deve ter resolução de metadados e build/package adequados; reutilize testes comportamentais somente quando suas entradas não mudaram.
4. Prepare changelog, instruções de upgrade/rollback, artefatos e destino. Fixe SHA e hashes disponíveis. Use `gabriel-release-smoke-test` para provar o artefato que será entregue; o checkout de desenvolvimento não o substitui.
5. Antes da publicação, revalide head, tags existentes, autoridade e CI exato. Se uma tag já existe, compare seu alvo e a publicação correspondente. Nunca mova uma tag publicada silenciosamente nem trate retry como permissão para sobrescrever artefato.
6. Publique pelo mecanismo documentado somente dentro da autorização. Em timeout, reconcilie tag, release e artefatos antes de repetir. Verifique o destino e o artefato realmente distribuído. Deploy, migrações e produção conservam seus gates próprios.
7. Confirme estado remoto e comportamento relevante. Execute limpeza autorizada. No Xlondz, preserve a regra de cleanup pós-merge do projeto; não remova worktree ativa, dirty ou com arquivos ignorados de usuário.

## Entrega
Versão, SHA, CI, artefatos/hash e destino, smoke efetivamente executado, aceite operacional e pendências. Distingua preparado, publicado e validado em produção. Não apresente release iniciada como concluída.
