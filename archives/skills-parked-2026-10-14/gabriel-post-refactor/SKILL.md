---
name: gabriel-post-refactor
description: "Revisar um refactor recente em busca de regressões, contratos esquecidos, cobertura inadequada e risco de flakiness."
---

# Revisão após refactor

## Objetivo
Encontrar consequências de uma reorganização recente. A entrada é o intervalo do refactor, não uma autorização para reformar todo o repositório.

1. Fixe base/head ou diff de trabalho. Use os commits relacionados, normalmente poucos commits recentes, sem um corte numérico que omita parte do refactor. Leia intenção e contratos anteriores.
2. Confira gates já executados e suas entradas. Rode apenas o delta necessário e os gates finais exigidos. Não execute conteúdo suspeito antes da revisão estática.
3. Trace chamadores após renomes/movimentos, imports/exports, registro de rotas, serialização, configurações e compatibilidade. Procure adaptadores deixados para trás, código morto, fontes de verdade duplicadas, helpers genéricos sem utilidade e documentação antiga.
4. Revise testes pelo que provam: assertivas sobre comportamento, não detalhes internos reorganizados; regressão real; mocks que não escondem integração quebrada; isolamento de fixtures. Examine tempo real, sleeps, ordem global, concorrência e recursos não fechados como causas concretas de flakiness.
5. Classifique achados como defeito, lacuna de prova ou melhoria opcional. Dê arquivo/linha, cenário e correção mínima. Não transforme gosto pessoal em bloqueio.
6. Corrija somente se a tarefa já autoriza ajustes. Revalide a superfície afetada e não reinicie toda a investigação a cada ajuste mecânico.

## Entrega
Intervalo, achados por impacto, riscos de cobertura/flakiness, checks e próximo passo. Use `gabriel-simplify` para simplificação solicitada; `gabriel-pr-post-audit` para interações de um lote de tickets, mesmo que contenha refactors.
