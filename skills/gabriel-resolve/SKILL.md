---
name: gabriel-resolve
description: "Implementar uma issue de escopo definido até código validado, preservando continuidade e gates do projeto."
---

# Resolver o trabalho autorizado

Leia as instruções do projeto e os critérios de aceite atuais. Reuse o executor/checkpoint da mesma issue. Preserve trabalho local existente; use isolamento quando necessário. Mantenha um responsável pela implementação e delegue apenas perguntas independentes ou revisões requeridas. Não crie novas tarefas no aplicativo sem autorização para isso.

Implemente a menor mudança que atende ao pedido. Para bug, reproduza o comportamento e acrescente regressão quando útil ou exigida; não crie testes que apenas espelham uma edição trivial. Não enfraqueça testes, silencie erros nem acrescente abstrações ou refactors sem necessidade do escopo.

Use testes focados durante a iteração e os gates finais do projeto no candidato correto. Reuse provas válidas; nova revisão, ambiente ou entrada invalida apenas as provas afetadas. Preserve o primeiro erro sanitizado. Se tentativas repetidas não trouxerem evidência nova, mude a hipótese ou reproduza o defeito do runner localmente antes de repetir a operação real.

Em operações externas, siga a sessão autorizada: recursos, prazo absoluto, limites cumulativos, tentativas e cleanup. Resultado de mutação desconhecido exige reconciliação antes de reenviar. A skill não autoriza merge, deploy, gastos, publicação, escrita em memória ou novo ambiente.

Conclua com mudança, evidência, limitações e próximo passo. Separe código pronto de aceitação em staging/produção. Liste individualmente o que ficou pendente. Atualize o checkpoint da tarefa quando houver pausa ou transferência; não converta estado transitório em memória durável. Aplique as permissões de cleanup já concedidas pelo projeto sem pedir de novo, preservando branches avançadas, worktrees ativas e arquivos do usuário.
