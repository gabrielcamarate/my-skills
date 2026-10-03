---
name: gabriel-fact-check
description: "Verificar alegações factuais de um texto contra fontes primárias e revisar a lógica sem tratar opiniões como fatos verificáveis."
---

# Checagem factual adversarial

1. Defina texto, público, data e escopo. Separe alegações verificáveis de opinião, preferência, hipótese e recomendação. Decomponha números, causalidade, comparações, citações e afirmações universais.
2. Monte um ledger enxuto: alegação, fonte primária, data/versão, trecho ou dado relevante, conclusão e confiança. Consulte fontes atuais para informação mutável. Ausência de resultado de busca não prova falsidade.
3. Classifique correta, falsa, imprecisa, enganosa por contexto ou não sustentada. Opiniões ficam fora da checagem factual, mas inferências apoiadas em premissa falsa merecem apontamento.
4. Faça uma passagem de lógica: denominadores, unidades, percentuais, seleção de amostra, comparabilidade, correlação/causalidade, generalização e conclusão que excede a fonte. Verifique links e citações; não invente referências nem transforme paráfrase em citação literal.
5. Corrija o texto se edição está autorizada, preservando voz e tese que a evidência sustenta. Caso contrário, entregue sugestões localizadas. Explique quando uma tese não sobrevive às fontes, sem diluir o problema com eufemismos.
6. Faça uma segunda passagem no texto corrigido, priorizando afirmações materiais e erros novos. Se houver verificador independente disponível e autorizado, forneça texto e fontes sem induzir resultado. Se feita pelo mesmo agente, declare autorrevisão; não simule um segundo modelo.
7. Registre buscas inconclusivas e limites de acesso. Não acione APIs pagas, fanout de modelos, exportação de texto privado ou publicação automaticamente. Custo desconhecido continua desconhecido, nunca zero.

## Entrega
Conclusão principal, correções materiais com fontes diretas, alegações sem evidência e versão corrigida quando solicitada. Mantenha opinião identificada e evite uma lista de “correto” que esconda os problemas relevantes.

## Ferramentas opcionais para este escopo

Para pacotes de documentos autorizados, `docjev` pode classificar categorias e sugerir intervalos de páginas. Isso ajuda localizar fontes, não verificar alegações. Conferir conteúdo/fronteiras antes de exportar ou usar documentos. Consulte [roteamento](../../docs/tool-routing.md#decisões-documentos-e-contratos) e o perfil OpenRouter do My Tools. Confirmar disponibilidade nesta sessão e preservar autorização dos dados/gates do projeto.
