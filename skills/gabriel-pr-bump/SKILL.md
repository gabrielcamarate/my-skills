---
name: gabriel-pr-bump
description: "Consolidar um lote autorizado de atualizações compatíveis de dependências e verificar o lockfile e o comportamento resultantes."
---

# Atualizações de dependências

## Objetivo
Atualizar um conjunto coerente de dependências com um gate do resultado composto, sem resolver PRs de bots mecanicamente um a um.

1. Leia política de atualização, gerenciador, versões resolvidas, manifestos e lockfile. Liste PRs autorizados e classifique compatíveis, major, migração e substituição de origem. Não inclua todo o backlog por associação.
2. Leia notas oficiais das versões e advisories relevantes. Examine diretas e transitivas alteradas: registry, integridade, licença exigida pelo projeto, git/path dependencies, ranges e scripts de instalação novos. Bloqueie origem inexplicável ou comportamento suspeito antes de instalar.
3. Forme um lote de atualizações compatíveis usando o gerenciador existente. Preserve constraints intencionais e runtimes suportados. Major ou migração sai do lote até haver escopo e plano próprios. Não edite o lockfile para fabricar resolução impossível.
4. Instale em ambiente apropriado à confiança do código. Confira diff de manifestos/lockfile, dependências inesperadas, scripts e superfície afetada. Investigue conflito pela causa; não amplie versões indiscriminadamente nem desative verificações.
5. Rode checks focados durante ajustes e o gate requerido uma vez no candidato final. Inclua build/package quando a atualização afeta empacotamento, e teste do caminho relevante quando afeta runtime. Registre versões antes/depois e checks reutilizados com justificativa.
6. Prepare a entrega do lote. Somente após publicação/integração autorizadas e confirmadas, reconcilie PRs substituídos e feche os que realmente perderam objeto, quando autorizado. Release e deploy são ações distintas.

## Saída
Tabela pacote, versão anterior/nova, origem, impacto e prova. Liste upgrades excluídos, motivo, lockfile final e estado real dos PRs. Não atribua resolução a um push ainda não verificado.
