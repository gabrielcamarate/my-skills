---
name: gabriel-release
description: "Preparar uma release ou executar uma publicação explicitamente autorizada, com revisão exata e aceite operacional."
---

# Release com alvo e evidência explícitos

Primeiro identifique se o pedido é preparar ou executar. Sem autorização para publicar, prepare um candidato concreto e revisável: revisão, destino, mudanças, gates, recuperação e pendências. Não peça aprovação de uma proposta vaga quando ainda puder preparar o material localmente.

Siga a skill e os scripts de release específicos do projeto quando existirem; este procedimento não substitui sequência staging/main, permissões ou revisões mandatórias. Revalide refs e a autorização imediatamente antes da ação consequente. Não publique tag, release, pacote, migração ou deploy por inferência de um pedido para terminar uma issue.

Classifique compatibilidade e versão conforme o contrato do projeto. Depois de alterações de versão/changelog, vincule os gates obrigatórios ao SHA final correspondente. Não reescreva tags publicadas. Reuse o mesmo artefato validado onde o pipeline suportar; trate a mudança do artefato como mudança relevante.

Prepare recuperação proporcional. Reverter código não desfaz cobranças nem remoção de dados; migrações precisam de estratégia própria. Durante execução autorizada, preserve limites cumulativos e reconcilie resultado desconhecido antes de retry.

Confirme versão/revisão implantada, saúde e jornada afetada, respeitando o ambiente autorizado. Registre separadamente código pronto e aceite operacional. Complete cleanup rotineiro já autorizado no projeto, sem remover trabalho ativo ou alterações locais. Reporte resultado e evidências, não apenas que o pipeline foi iniciado.
