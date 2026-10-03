# Feedback cedo, sem duplicar gates

1. Resolva cedo os pré-requisitos do aceite: runtime, alvo, autenticação sintética,
   fixture/proveniência e ferramenta. Fonte ausente no env não prova ausência no
   host; use locators do projeto, sem expor segredos ou ampliar autorização.
2. Para o contrato externo que mudou, prove uma interação mínima com a versão
   real antes de expandir implementação/testes/revisão. Mock permissivo e SQL
   isolado não provam SDK nem resposta HTTP. Reutilize harness/recursos aprovados;
   registre limitações sem inventar PASS ou construir infraestrutura incidental.
3. Na UI, preserve o design aprovado e inspecione estados/transições afetados
   localmente antes da primeira integração quando suportado. Diálogos/foco/erro
   e viewport pertinente entram apenas quando afetados. Aceite remoto continua.
4. Iteração usa testes conhecidos e execução única. Watch é interativo explícito,
   nunca gate. Reutilize CI correspondente aos mesmos inputs quando o projeto
   permite; não repetir suíte ampla para preencher recibo, após aprovação ou
   interrupção. Falha local fica registrada: defeito de produto bloqueia;
   falha do runner exige investigação focada, não outra suíte por reflexo.
5. Antes de publicação, use o preflight determinístico já fornecido pelo projeto
   para corpo/metadados/release no candidato exato. Valide a descrição real;
   não chamar CI para descobrir formatação ou nota de follow-up ausente.
   Não introduza um hook universal ou outro validador concorrente.
6. Identifique no início quem usa o checkout compartilhado e a rota disponível de
   coordenação. Não pedir ao usuário que adivinhe o estado de outra thread.
   Sincronização bloqueada exige responsável/ação no recibo; se não é critério
   de produto, não refazer QA nem manter issue artificialmente aberta. Nunca
   declarar workflow completo com pendência, presumir liberação ou enviar
   mensagens sem autorização.

Use o ledger existente; essa sequência não cria outra skill, revisão, monitor ou
permissão. Gates de segurança, head final, staging/produção, ownership e cleanup
continuam. Rerun precisa de input alterado ou falha relevante identificada, não
apenas tempo decorrido. Ganho de tempo exige comparação posterior equivalente.
