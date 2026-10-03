---
name: gabriel-humanizer
description: "Revisar a linguagem de um texto para eliminar artificialidade e preservar significado, fatos, incerteza e voz do autor."
---

# Edição de linguagem natural

Fase experimental obrigatória: ao ocorrer um gatilho desta skill, execute a ferramenta oficial indicada antes de substituir pela rota habitual. Leia somente a linha pertinente do [roteamento](references/tool-routing.md), que define gatilhos e dispensas. Ler a skill ou consultar `--help` não conta como uso. Registre chamada/resultado ou dispensa concreta no checkpoint existente e resuma isso na entrega; falha da ferramenta pede fallback, não abandono da tarefa.

## Objetivo
Deixar o texto mais direto e legível, conservando conteúdo e intenção. Não é checagem de fatos nem licença para inventar experiências pessoais.

1. Leia o texto inteiro, público e voz desejada. Preserve termos técnicos necessários, números, links, ressalvas e afirmações que o autor realmente fez. Para representar Gabriel externamente, prepare o rascunho para revisão conforme suas instruções.
2. Procure padrões que atrapalham a leitura, usando [o guia de edição](references/patterns.md) quando necessário. Corrija ocorrências concretas, sem proibir palavras só porque aparecem numa lista.
3. Troque dramatização, frases genéricas, qualificadores vazios e autoridade vaga por proposições específicas já sustentadas no texto. Se faltam dados, não preencha com invenção.
4. Varie ritmo conforme o raciocínio. Remova contrastes artificiais, trios forçados, títulos decorativos e negrito sem função. Preserve listas e seções quando ajudam a comparar ou navegar.
5. Ajuste ao pt-BR direto de Gabriel quando esse for o autor: linguagem concreta, sem travessões ou elogios vazios. Não imite a personalidade do Akita nem injete opinião agressiva para parecer humano.
6. Releia a versão final contra o original: houve perda de significado, mudança de certeza, afirmação nova, promessa exagerada ou referência removida? Reverta alterações sem base.

## Entrega
Texto editado; explicação breve só para mudanças materiais ou quando pedida. Se houver dúvida factual, sinalize ou encaminhe a `gabriel-fact-check`; não transforme edição de estilo em validação factual implícita.

## Ferramentas obrigatórias nos gatilhos deste escopo

Para rascunho com vários parágrafos e regras de estilo existentes adequadas ao idioma, execute a CLI `snifftest` conforme a skill upstream antes da revisão editorial. Confira cada alerta e preserve o significado; o teste sintético não comprovou precisão em português. Não criar um conjunto de regras ou enviar conversa privada só para chamar a ferramenta. Veja [gatilhos e dispensas](references/tool-routing.md#decisões-documentos-e-contratos).
