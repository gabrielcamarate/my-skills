---
name: gabriel-pr-post-audit
description: "Auditar o efeito composto de um lote de mudanças para detectar interações que revisões individuais não cobrem."
---

# Auditoria do lote composto

## Escopo
Use após um lote relacionado ou como gate de `gabriel-github-resolution` com mais de três tickets de código. Analise a composição entre base confiável e candidato final, não o histórico inteiro do produto.

1. Fixe base/head e alterações locais relevantes. Relacione tickets, commits, auditorias individuais e contratos alterados. Se a última release não é a base adequada, use o último marco revisado e explique a escolha.
2. Confira que cada recomendação aprovada entrou e cada pendência continua visível. Verifique autoria, dependências entre mudanças, regressões reintroduzidas e efeitos cancelados por commits posteriores.
3. Revise o diff composto com o trust gate de [referência](references/composition.md). Mudanças inocentes isoladas podem habilitar execução, exposição ou quebra em conjunto.
4. Trace interações: produtor/consumidor, schema/migração, cache/tenant, autenticação/autorização, filas/retries, ordenação, configuração/defaults e lifecycle/cleanup. Procure políticas duplicadas, código morto e dependências que ficaram sem uso.
5. Confira documentação e changelog: o contrato final está descrito; mudanças pendentes estão fora de seções publicadas; breaking changes não estão escondidas como patch. Não reescreva registros históricos para parecerem atuais.
6. Monte a verificação do conjunto reutilizando resultados ainda válidos. Execute provas novas para fronteiras cruzadas e os gates obrigatórios do candidato final. Corrija achados somente dentro do escopo autorizado e reavalie o que a correção afetou.

## Entrega
Intervalo auditado, tickets cobertos, achados com evidência, alegações reconciliadas, checks válidos, lacunas e parecer para a próxima etapa. Não publique nem lance a release por consequência da auditoria.
