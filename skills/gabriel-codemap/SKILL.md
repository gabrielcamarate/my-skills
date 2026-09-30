---
name: gabriel-codemap
description: "Criar ou atualizar um mapa arquitetural de um repositório quando solicitado ou quando a orientação persistente for necessária."
---

# Mapa do repositório

## Objetivo
Produzir um atlas de responsabilidades e fluxos, não uma listagem de arquivos. Não ativar para localizar uma função ou fazer uma edição pequena.

1. Procure mapa, documentação e índice existentes. Identifique revisão e entradas que os sustentam. Atualize a fonte canônica, evitando um segundo atlas concorrente.
2. Inventarie arquivos com `rg --files` ou `git ls-files` e respeite exclusões do projeto. Exclua segredos, dumps, dependências vendorizadas e builds. Não percorra todo o disco nem inclua conteúdo privado no mapa. Não habilite captura de memória.
3. Leia entrypoints, manifests e módulos relevantes. Para cada região, explique responsabilidade, decisões de desenho, fluxo, interfaces e integrações. Relacione chamadas reais a caminhos verificáveis; nome de pasta não comprova arquitetura.
4. Mostre como uma entrada importante atravessa o sistema e onde as regras centrais vivem. Destaque ownership e fronteiras. Uma área não lida deve aparecer como lacuna, não ganhar uma descrição inventada.
5. Salve o mapa no lugar de documentação já adotado quando a tarefa autoriza a escrita. Registre revisão, data, arquivos-base e modo de atualização. Se existem hashes/manifesto incremental, compare apenas entradas relevantes e preserve regiões sem mudança; git diff e identidade das entradas podem cumprir o mesmo papel sem um daemon.
6. Faça links relativos navegáveis. Inclua rota no AGENTS/CLAUDE somente quando a mudança dessas instruções está dentro do escopo, mantendo a paridade que o projeto exigir.

## Busca de código com my-tools
Quando precisar localizar um comportamento sem conhecer nomes exatos, execute `my-tools --project RAIZ status`. Se search estiver habilitado, permitir envio remoto e possuir uma lista não vazia de `globs` autorizados, prefira `my-tools --project RAIZ search "comportamento procurado" --top 5 --json --stats`. O launcher aplica o escopo salvo; não amplie padrões nem habilite envio por conta própria. Não envie credenciais, dados privados ou consultas com conteúdo sensível.

Use `rg` para símbolos, caminhos e mensagens exatos, ou quando o launcher estiver ausente, bloqueado, falhar ou não trouxer evidência suficiente. Leia os arquivos e chamadores relevantes para confirmar o resultado; ranking não prova comportamento nem cobre todo o código. Reutilize contexto já conhecido, sem repetir busca apenas para cumprir esta orientação. Mencione o uso e eventuais limites na entrega; economia só pode ser afirmada com medição comparável.

## Entrega
Atlas com entrada do sistema, mapa de diretórios por responsabilidade, fluxos, integrações, fontes e lacunas. Informe o que mudou na atualização e sua validade. Não crie agentes por pasta ou arquivos de estado do OpenCode em um runtime que não os usa.
