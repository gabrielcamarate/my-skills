---
name: gabriel-reflect
description: "Analisar atrito recorrente do workflow e propor a menor melhoria reutilizável sustentada por evidência real."
---

# Reflexão sobre o workflow

## Objetivo
Transformar repetição custosa em uma melhoria pequena, sem construir novas regras para toda exceção.

1. Reúna ocorrências concretas: tarefa, repetição, custo/espera, intervenção e consequência. Use os registros existentes e o escopo autorizado. Uma impressão isolada não prova gargalo; incidente grave pode justificar correção única com motivo explícito.
2. Inventarie skills, scripts, documentação, gates e decisões já existentes. Procure regra mal descoberta ou instrução duplicada antes de propor outra skill. Verifique causa do atrito: informação, ferramenta, processo ou decisão humana necessária.
3. Compare candidatos por frequência, custo, risco, estabilidade e cobertura existente. Separe medição de estimativa. Não prometa economia de tokens/tempo sem comparação adequada.
4. Escolha a menor forma útil: remover passo, corrigir descrição/roteamento, documentar comando, escrever script determinístico, ajustar skill, criar skill de objetivo distinto ou não mudar nada.
5. Apresente evidência, mudança, ganho esperado, risco, validação e reversão. Se a tarefa já autoriza a melhoria local, implemente-a sem uma segunda aprovação ritual. Caso contrário, entregue proposta concreta. Escrita em memória, captura, projetos consumidores ou publicação precisam da autoridade correspondente.
6. Valide pelo comportamento que falhava. Registro estrutural ou contagem de skills não demonstra eficiência. Agende acompanhamento apenas quando solicitado e usando a automação já existente quando aplicável.

## Entrega
Uma melhoria escolhida ou motivo para não mudar; antes/depois verificável; escopo alterado; evidência e limites. Conhecimento durável vai à fonte canônica autorizada; estado transitório continua no checkpoint.
