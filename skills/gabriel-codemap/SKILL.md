---
name: gabriel-codemap
description: "Criar ou atualizar um mapa arquitetural de um repositório quando solicitado ou quando a orientação persistente for necessária."
---

# Mapa do repositório

Antes de uma operação elegível, siga a [escolha de ferramentas](../../docs/tool-routing.md); registre no checkpoint existente a interface usada ou o motivo concreto do fallback.

## Objetivo
Produzir um atlas de responsabilidades e fluxos, não uma listagem de arquivos. Não ativar para localizar uma função ou fazer uma edição pequena.

1. Procure mapa, documentação e índice existentes. Identifique revisão e entradas que os sustentam. Atualize a fonte canônica, evitando um segundo atlas concorrente.
2. Inventarie arquivos com `rg --files` ou `git ls-files` e respeite exclusões do projeto. Exclua segredos, dumps, dependências vendorizadas e builds. Não percorra todo o disco nem inclua conteúdo privado no mapa. Não habilite captura de memória.
3. Leia entrypoints, manifests e módulos relevantes. Para cada região, explique responsabilidade, decisões de desenho, fluxo, interfaces e integrações. Relacione chamadas reais a caminhos verificáveis; nome de pasta não comprova arquitetura.
4. Mostre como uma entrada importante atravessa o sistema e onde as regras centrais vivem. Destaque ownership e fronteiras. Uma área não lida deve aparecer como lacuna, não ganhar uma descrição inventada.
5. Salve o mapa no lugar de documentação já adotado quando a tarefa autoriza a escrita. Registre revisão, data, arquivos-base e modo de atualização. Se existem hashes/manifesto incremental, compare apenas entradas relevantes e preserve regiões sem mudança; git diff e identidade das entradas podem cumprir o mesmo papel sem um daemon.
6. Faça links relativos navegáveis. Inclua rota no AGENTS/CLAUDE somente quando a mudança dessas instruções está dentro do escopo, mantendo a paridade que o projeto exigir.

## Ferramentas oficiais do Siftr (MCP)
Antes da primeira busca, escolha pela evidência já disponível: com arquivo/trecho confirmado, leia diretamente; com símbolo ou mensagem exata, use `rg`; com apenas uma descrição do comportamento e sem localização confirmada, use primeiro `semantic_search` do MCP Siftr. Uma pasta presumida não é localização confirmada. Não faça várias buscas locais para depois cumprir esta orientação; não repita descoberta quando o contexto já basta.

Use `focused_read` quando precisar de uma parte de arquivo grande, e `pick_relevant` para priorizar uma lista de testes ou arquivos, preservando os gates obrigatórios. `filter_output` é experimental e lê um arquivo de saída existente; use apenas logs sintéticos ou saneados e autorizados. Identifique o servidor Siftr se houver ferramentas homônimas.

O MCP oficial precisa estar conectado na sessão e usa as ferramentas upstream sem proxy. Passe caminhos explícitos e filtros de código autorizados; nunca envie credenciais, dados financeiros/de clientes, documentos privados ou consultas sensíveis. O MCP não impõe isolamento ou allowlist por projeto. Não instale nem amplie permissões por conta própria.

Se o MCP estiver ausente, falhar ou trouxer evidência insuficiente, use `rg` e leitura direta e relate o limite. Confira implementação e chamadores; ranking não prova comportamento nem ausência de código. Registre chamadas e resultado quando houver avaliação; economia exige comparação equivalente.

## Entrega
Atlas com entrada do sistema, mapa de diretórios por responsabilidade, fluxos, integrações, fontes e lacunas. Informe o que mudou na atualização e sua validade. Não crie agentes por pasta ou arquivos de estado do OpenCode em um runtime que não os usa.
