---
name: gabriel-verification-planning
description: "Definir ou reconciliar a evidência necessária para provar uma mudança não trivial, incluindo validade de verificações anteriores."
---

# Planejamento de verificação

Antes de afirmar contratos atuais, confirme base/SHA e leia instruções/guias na mesma revisão de trabalho; atualizar refs não atualiza um checkout antigo. Preserve trabalho dirty/ativo. Para contratos alterados, identifique os guias existentes, atualize-os no mesmo PR e registre paths/dispensas específicas; README/changelog não substituem documentação de domínio. Confronte texto com código/testes no candidato final e reutilize evidência válida.

Para implementação não trivial, siga o [feedback antecipado](../../docs/fast-feedback.md): pré-requisitos e integração real cedo, testes em execução única, reuso de CI válido e preflight documental do projeto antes de publicação. Preserve gates e autoridade.

## Objetivo
Transformar uma alegação de entrega em evidência observável com custo proporcional. Não é uma suite universal de testes.

1. Expresse a alegação, entradas, ambiente, fronteiras e invariantes que devem permanecer. Identifique o erro mais importante que um falso PASS esconderia.
2. Inventarie evidência existente: revisão, arquivos/entradas relevantes, configuração, ambiente, horário, resultado e limitações. Reutilize somente enquanto essas condições continuarem válidas e as regras do projeto permitirem. Gate obrigatório do head final permanece obrigatório.
3. Compare caminhos possíveis: teste de lógica, integração, inspeção de artefato, UI renderizada, estado remoto ou medição operacional. Escolha o caminho mais barato que realmente diferencia sucesso de falha. Um build não prova comportamento visual; um usuário não prova cinco simultâneos.
4. Atribua uma fonte responsável por cada alegação e evite verificações duplicadas. Defina critério de aprovação, resultado inconclusivo, invalidação e orçamento de execução. Para operação real, explicite ambiente, recursos próprios, expiração, custos/tráfego, tentativas, falhas recuperáveis, paradas críticas e limpeza.
5. Se falta observabilidade, escolha a menor instrumentação necessária e seu ciclo de vida. Aproveite fixtures e ferramentas existentes. Mudanças estruturais, persistência ou dependências fora do escopo não são consequência automática de querer evidência.
6. Torne o caminho reproduzível. Registre comandos confiáveis e parâmetros não sensíveis. Preserve a primeira falha antes de limpeza. Teste localmente defeitos do runner antes de pedir outra janela remota.
7. Interprete os resultados contra a alegação: estabelecida, limitada ou refutada. Diferencie falha da medição, falha do produto e falha de cleanup. Apresente a próxima evidência que resolve uma lacuna.

## Saída
Use o registro existente da tarefa: alegação → fonte/comando → candidato e ambiente → resultado → limites/invalidação. Não crie um segundo ledger ou monitor quando o projeto já possui um.
