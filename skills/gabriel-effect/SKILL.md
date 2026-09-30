---
name: gabriel-effect
description: "Trabalhar em código TypeScript que já usa Effect, verificando APIs e padrões contra a versão efetivamente instalada."
---

# Effect

## Escopo
Aplique apenas a projetos que já usam Effect ou cuja adoção foi explicitamente solicitada. Esta skill não recomenda migrar outros projetos para Effect por associação.

1. Confirme versão resolvida, arquitetura e helpers de teste existentes. O original foi escrito para Effect v4/effect-smol; não assuma que esse é o ambiente atual.
2. Consulte documentação e fontes oficiais da versão aplicável. Use `gabriel-clonedeps` quando precisar da implementação. Verifique cada API sensível à versão, em vez de transportar exemplos v2/v3/v4 por semelhança de nome.
3. Siga o estilo do projeto para composição de efeitos, serviços e layers. Mantenha handlers finos, contratos e erros de domínio tipados e provisioning explícito. Não introduza casts, `any` ou assertions para esconder incompatibilidade.
4. Use as abstrações Effect já adotadas para recursos, cancelamento e concorrência; evite criar runtimes paralelos ou promises que escapem do lifecycle. Verifique sucesso, erro, interrupção e finalização.
5. Teste com layers e helpers locais. Recursos reais de filesystem, sockets, processos, locks ou relógio exigem o modo de teste compatível com operações reais na versão instalada. Não copie um caminho de teste de outro repositório.
6. Execute comandos do pacote correto e os gates do projeto. Explique provisão de dependências e ownership de recursos no diff.

## Saída
Mudança, versão consultada, fonte da API, testes e limites. Se não há Effect no escopo, não carregue esta skill para código TypeScript comum.
