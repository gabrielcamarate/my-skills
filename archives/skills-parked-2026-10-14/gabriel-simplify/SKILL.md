---
name: gabriel-simplify
description: "Simplificar código já compreendido preservando comportamento, contratos, ordem de efeitos e convenções do projeto."
---

# Simplificação de código

## Objetivo
Facilitar entendimento e manutenção sem alterar comportamento. Reduzir linhas, por si só, não é ganho.

1. Delimite a superfície solicitada ou recém-alterada. Entenda responsabilidade, chamadores, efeitos, erros, concorrência e razão das abstrações existentes. Se não entende o comportamento, investigue antes de editar.
2. Compare com convenções vizinhas. Procure aninhamento desnecessário, nomes vagos, duplicação verdadeira, wrappers sem valor e responsabilidades misturadas. Preserve nomes e abstrações que carregam intenção ou permitem testar o sistema.
3. Faça uma mudança coerente por vez. Prefira controle de fluxo claro a expressões compactas. Não junte responsabilidades só por semelhança textual e não crie uma abstração genérica para um caso único.
4. Verifique preservação de entradas/saídas, efeitos e sua ordem, exceções, defaults, cancelamento, performance relevante e contratos públicos. Se a equivalência não pode ser sustentada, trate como mudança de comportamento com escopo próprio.
5. Rode checks relevantes; testes existentes não devem ser enfraquecidos para acomodar o refactor. Adicione prova somente quando falta cobertura material. Reutilize gates ainda válidos e cumpra os finais exigidos pelo projeto.

## Saída
Diff restrito, motivo da simplificação, evidência de equivalência e limitações. Deixe código já claro como está. Mudança de arquitetura pertence a `gabriel-improve-codebase-architecture`; auditoria do refactor entregue pertence a `gabriel-post-refactor`.
