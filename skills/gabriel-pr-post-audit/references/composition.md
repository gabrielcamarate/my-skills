# Fronteiras de composição

Revise o intervalo composto antes de executar conteúdo novo ou desconhecido.
Uma dependência adicionada por um PR pode receber credenciais introduzidas por
outro. Um workflow pode publicar um artefato que outro PR passou a buscar de
origem substituível. Confira essas ligações, além da inspeção de cada arquivo.

| Interação | Pergunta que decide a revisão |
|---|---|
| API e consumidor | O contrato final é o mesmo dos dois lados, inclusive erro e default? |
| Schema e migração | A ordem de rollout suporta leitores/escritores antigos e novos? |
| Tenant e cache | A chave mantém a mesma identidade de isolamento em todos os caminhos? |
| Autenticação e rota | Alguma rota nova contorna middleware ou autorização por objeto? |
| Retry e persistência | Reenvio após timeout cria duplicação ou ultrapassa orçamento? |
| Recurso e cleanup | Quem cria, retém e destrói? Cancelamento deixa ownership claro? |
| Flags e defaults | Desligar uma feature mantém as invariantes necessárias? |
| Dependência e build | O pacote final resolve e inclui o que o runtime espera? |
| UI e backend | Payload, erro e loading correspondem ao contrato realmente entregue? |

Não crie um teste para cada linha por hábito. Escolha as linhas afetadas e a prova
capaz de distinguir o defeito. Registre as demais como fora de escopo quando isso
importar. Um achado do lote deve apontar quais mudanças interagem e como a falha
ocorre; “pode haver regressão” não basta.

Reconcile documentação com o resultado final e mantenha changelog publicado
imutável. Preserve evidência por ticket, mas não use uma coleção de checks verdes
isolados como prova automática de que o conjunto funciona.
