---
name: gabriel-verify
description: "Planejar ou reconciliar verificações de uma entrega, identificando provas válidas, lacunas e critérios de aceite."
---

# Provar o comportamento relevante

Parta dos critérios de aceite e dos gates obrigatórios do projeto. Para cada alegação relevante, escolha a evidência observável e o caminho mais barato que realmente a comprova. Procure testes, fixtures, scripts, CI e evidência já existentes antes de criar infraestrutura.

Associe resultados a revisão, dirty diff quando relevante, ambiente, entradas, comando, horário e saída ou link. Descreva o que invalida cada prova. Não trate pending, skipped, saída sem conteúdo ou ausência de erro como PASS. CI equivalente pode satisfazer o gate local somente quando as regras do projeto permitirem e candidato/entradas corresponderem.

Durante alterações, execute checks focados. Execute o conjunto final obrigatório uma vez no candidato final e repita só o afetado por uma mudança ou falha. Compilar não prova comportamento em outra plataforma; testar o código-fonte não prova o pacote distribuído; screenshot não prova persistência no backend.

Para UI, verifique a renderização e a interação afetada com dados coerentes. Para fronteiras de acesso ou idempotência, tente a violação e inclua um controle legítimo. Para deploy, confira o artefato e o ambiente realmente entregues. Operações reais seguem a autorização existente; não provisione recursos só para tranquilizar o relatório.

Entregue uma tabela curta: alegação, prova, candidato/ambiente, resultado e lacuna. Use as distinções do projeto entre código pronto, staging aceito e produção aceita. Não invente custos ou tokens; diferencie duração total, trabalho ativo e espera, sem somar intervalos sobrepostos.
