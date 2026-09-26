---
name: gabriel-deepwork
description: "Coordenar trabalho grande ou de alto risco em fases dependentes com revisões delimitadas. Não usar para mudanças rotineiras em vários arquivos."
---

# Trabalho complexo em fases

## Critério de uso
Migração que não pode ser entregue parcialmente, mudança estrutural ampla ou fases dependentes com ownership especializado. Vários arquivos, por si só, não justificam este procedimento.

1. Defina objetivo, invariantes, fases entregáveis e dependências antes de executar. Registre um gate por risco material de cada fase. Reutilize o checkpoint e executor existentes, sem criar tarefas ou agentes por inferência.
2. Quando há delegação disponível e autorizada, o coordenador distribui responsabilidade e reconcilia resultados; não disputa os mesmos arquivos com executores. Escolha caminhos paralelos somente se independentes. Sem essa capacidade, execute as fases sequencialmente e declare a ausência de revisão independente.
3. Mantenha estado no mecanismo da tarefa/projeto: revisão, caminho, dirty state, decisões, evidências válidas, autorizações, executores e watcher/cursor. Use arquivo local apenas quando necessário e autorizado; não imponha `.slim` nem converta checkpoint em memória durável.
4. Antes de cada fase, passe contrato, entradas, escopo de arquivos, prova esperada e risco a revisar. Preserve decisões visuais aceitas; alterações mecânicas posteriores não autorizam redesenho.
5. Aguarde e reconcilie todos os resultados dependentes antes de avançar. Use eventos e esperas limitadas, um watcher por execução e a medição já configurada pelo projeto. Não crie heartbeat ou polling duplicados.
6. Aplique revisão prevista em cada fase: uma inicial e até duas novas revisões somente para correção que muda risco/decisão ou deixa prova pendente. Não use uma nova revisão para reabrir assunto inalterado. Ao esgotar o orçamento com problema material, registre a decisão que falta; não declare aprovação por cansaço.
7. Faça validação focada das correções e gate final do conjunto. Se gate independente é obrigatório e indisponível, prepare o restante da entrega e reporte essa lacuna sem substituir por autorrevisão rotulada como independente.

## Entrega
Resultado por fase, revisões realmente realizadas, candidato, evidência final, bloqueios e próximo passo. Despacho de executor não equivale a conclusão.
