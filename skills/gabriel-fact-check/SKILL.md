---
name: gabriel-fact-check
description: "Verificar alegações factuais de um texto contra fontes primárias e revisar a lógica sem tratar opiniões como fatos verificáveis."
---

# Checagem factual adversarial

Fase experimental obrigatória: ao ocorrer um gatilho desta skill, execute a ferramenta oficial indicada antes de substituir pela rota habitual. Leia somente a linha pertinente do [roteamento](references/tool-routing.md), que define gatilhos e dispensas. Ler a skill ou consultar `--help` não conta como uso. Registre chamada/resultado ou dispensa concreta no checkpoint existente e resuma isso na entrega; falha da ferramenta pede fallback, não abandono da tarefa.

1. Defina texto, público, data e escopo. Separe alegações verificáveis de opinião, preferência, hipótese e recomendação. Decomponha números, causalidade, comparações, citações e afirmações universais.
2. Monte um ledger enxuto: alegação, fonte primária, data/versão, trecho ou dado relevante, conclusão e confiança. Consulte fontes atuais para informação mutável. Ausência de resultado de busca não prova falsidade.
3. Classifique correta, falsa, imprecisa, enganosa por contexto ou não sustentada. Opiniões ficam fora da checagem factual, mas inferências apoiadas em premissa falsa merecem apontamento.
4. Faça uma passagem de lógica: denominadores, unidades, percentuais, seleção de amostra, comparabilidade, correlação/causalidade, generalização e conclusão que excede a fonte. Verifique links e citações; não invente referências nem transforme paráfrase em citação literal.
5. Corrija o texto se edição está autorizada, preservando voz e tese que a evidência sustenta. Caso contrário, entregue sugestões localizadas. Explique quando uma tese não sobrevive às fontes, sem diluir o problema com eufemismos.
6. Faça uma segunda passagem no texto corrigido, priorizando afirmações materiais e erros novos. Se houver verificador independente disponível e autorizado, forneça texto e fontes sem induzir resultado. Se feita pelo mesmo agente, declare autorrevisão; não simule um segundo modelo.
7. Registre buscas inconclusivas e limites de acesso. Não acione APIs pagas, fanout de modelos, exportação de texto privado ou publicação automaticamente. Custo desconhecido continua desconhecido, nunca zero.

## Entrega
Conclusão principal, correções materiais com fontes diretas, alegações sem evidência e versão corrigida quando solicitada. Mantenha opinião identificada e evite uma lista de “correto” que esconda os problemas relevantes.

## Ferramentas obrigatórias nos gatilhos deste escopo

Quando o trabalho exigir classificar um pacote de documentos/páginas em categorias já definidas, use `docjev classify`; use split somente se separar páginas fizer parte do pedido. Confirme conteúdo e fronteiras antes de exportar. DocJev localiza fontes, não verifica alegações. Uma página conhecida não exige classificação. Veja [gatilhos e dispensas](references/tool-routing.md#decisões-documentos-e-contratos).
