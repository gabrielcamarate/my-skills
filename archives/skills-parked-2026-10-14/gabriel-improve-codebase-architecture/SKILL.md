---
name: gabriel-improve-codebase-architecture
description: "Investigar fronteiras de módulos e propor uma mudança estrutural que reduza acoplamento e custo real de manutenção."
---

# Melhorar arquitetura

## Objetivo
Encontrar uma fronteira de módulo que esconda complexidade atrás de uma interface pequena e estável. A quantidade de camadas ou arquivos não mede qualidade.

1. Leia objetivos, decisões arquiteturais aceitas e restrições. Identifique uma dor concreta: mudança que atravessa muitos módulos, regra duplicada, interface extensa, dependência invertida ou testes caros por falta de uma fronteira.
2. Explore entradas, fluxo de dados, direção de dependências e ownership. Entenda o que muda junto. Use `gabriel-codemap` somente se a orientação do repositório justificar um mapa persistente.
3. Compare poucas alternativas relevantes, incluindo manter o desenho atual. Avalie profundidade do módulo, tamanho da interface, compatibilidade, isolamento de teste, migração e possibilidade de remover a abstração sem espalhar detalhes.
4. Apresente candidatos com dor/evidência, contrato proposto, arquivos afetados, benefício esperado, custo e risco. Prefira uma mudança localizada que esconda conhecimento a uma arquitetura genérica que exige mais coordenação.
5. Resolva apenas decisões ainda abertas por perguntas focadas. Não interrogue novamente sobre escolhas confirmadas nem trate toda alternativa técnica como pedido obrigatório de permissão.
6. Para implementação já autorizada, defina um corte que preserve comportamento, migração e prova. Decisão nova de produto ou expansão de escopo precisa ser resolvida antes da parte dependente.

## Entrega
Proposta ou mudança escolhida, alternativas rejeitadas com motivo, contrato, caminho de migração e validação. Registre decisão durável somente na fonte e dentro da autorização apropriadas; não escreva em memória por consequência desta skill.
