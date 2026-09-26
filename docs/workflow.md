# Workflow de entrega

## Responsabilidades

- Gabriel OS: prioridades, roteamento, decisões e acompanhamento necessário.
- Executor do projeto: contexto da issue, implementação, verificações e resultado.
- Revisor: pergunta independente ou gate exigido pelo risco e pelo projeto.
- Gabriel: decisões de produto e autorizações consequentes que ainda não existam.

Retome a mesma tarefa quando seu executor estiver disponível. Não invente outro
orquestrador, filas ou watchers. Preserve os checkpoints e a medição já existentes.

## Ciclo cotidiano

1. Identifique projeto, issue, executor e resultado esperado.
2. Reaproveite instruções, checkpoint e evidência; confirme o que pode ter mudado.
3. Faça triagem quando a causa ou o escopo ainda não estiver claro.
4. Implemente a mudança necessária, com verificações focadas durante a iteração.
5. Aplique a revisão e os gates obrigatórios do projeto no candidato final.
6. Prepare a entrega e execute apenas as operações já autorizadas.
7. Confirme o comportamento no ambiente entregue e conclua o cleanup autorizado.

Edição simples não precisa passar por seis skills. A revisão não autoriza merge.
Código validado não comprova staging ou produção. Um pipeline iniciado não é entrega.

## Evidência mínima reutilizável

Registre junto à tarefa: alegação/critério, candidato e alterações locais relevantes,
ambiente/entradas, comando ou fonte, horário, resultado, limitações e invalidação.
Não crie mais um ledger se o projeto já tem um. Reutilize CI equivalente quando permitido.

## Conhecimento e instruções

Instruções atuais do projeto definem os comandos e gates. Memória ajuda a encontrar
decisões e causas anteriores, mas não concede autoridade nem demonstra estado atual.
Mantenha decisões estáveis na fonte canônica autorizada. Checkpoints ficam na tarefa.
Este repositório fornece procedimentos reutilizáveis, sem copiar runbooks privados.

## Dependências e mudanças compostas

Quando houver uma fila autorizada de atualizações compatíveis de dependências,
considere um lote pequeno e uma verificação do conjunto. Confira registry, origem,
lockfile e scripts novos. Major, migração ou mudança de comportamento requerem escopo
próprio. Use o gerenciador do projeto. Não encerre PRs nem publique por inferência.
Após várias alterações relacionadas, revise suas interações se houver risco concreto.

## Melhorar sem interromper a entrega

Use gabriel-reflect quando houver evidência de atrito. Priorize eliminar uma repetição,
encurtar um diagnóstico ou tornar um comando previsível. As medidas são tempo até aceite,
retrabalho, espera, intervenções e regressões; contagem de skills não mede eficiência.
