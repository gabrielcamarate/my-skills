# Workflow de entrega

## Direção

O responsável pelo projeto coordena prioridades e continuidade. O executor entrega
o escopo autorizado com evidência; o usuário decide produto e ações consequentes
ainda não autorizadas. Regras, serviços, prioridades e autorizações particulares
ficam nas instruções do projeto consumidor, não neste pacote público.

A correspondência com Akita é de procedimentos e separação de responsabilidades,
com adaptações documentadas. Não copiamos um runtime inteiro nem assumimos que
suas autorizações pessoais valem nos nossos projetos.

## Ciclo principal

| Entrada | Procedimento | Saída que permite avançar |
|---|---|---|
| Issue ou bug ainda não explicado | `gabriel-iss-audit` | Diagnóstico, decisão e menor correção |
| PR para avaliação | `gabriel-pr-audit` | Parecer sobre base/head fixados |
| Mudança não trivial | `gabriel-verification-planning` | Alegações e prova observável com orçamento |
| Correção aprovada e autorizada | `gabriel-github-resolution` | Código, gates e entrega dentro da autoridade |
| Lote de mais de 3 tickets de código | `gabriel-pr-post-audit` | Interações verificadas no candidato composto |
| Atualizações compatíveis aprovadas | `gabriel-pr-bump` | Lote de dependências e lockfile verificados |
| Candidato a lançamento | `gabriel-release` | Versão/artefato preparados; publicação se autorizada |
| Artefato pronto | `gabriel-release-smoke-test` | Prova do caminho real de consumo |
| Atrito recorrente | `gabriel-reflect` | Melhoria mínima sustentada por evidência |

Auditoria e execução continuam distintas. Não é preciso carregar todas as skills
para executar uma fase. Uma skill pode ter vários passos que convergem no mesmo
resultado, como investigar, reproduzir e decidir uma issue.

## Especialidades

- `simplify` altera expressão sem alterar comportamento; `post-refactor` revisa
  as consequências de uma reorganização; `improve-codebase-architecture` trata
  fronteiras e contratos. Não são três nomes para a mesma revisão.
- `codemap` produz orientação persistente; `clonedeps` resolve dúvidas na fonte
  de dependências. Não são passos obrigatórios ao abrir qualquer repositório.
- `security-audit` aprofunda fronteiras de segurança quando o escopo exige.
- `deepwork` coordena fases complexas; `worktrees` gerencia isolamento de arquivos;
  `loop-engineering` limita tentativas com sucesso/parada observáveis.
- `agent-browser` interage com UI e verifica renderização; `effect` só se aplica
  à tecnologia presente ou à adoção solicitada.
- `fact-check` verifica fatos; `humanizer` edita linguagem; `blog-cost-charts`
  visualiza dados comparáveis. Não são carregadas como parte de toda entrega.

Todos os nomes usam prefixo `gabriel-`. Os plugins continuam disponíveis pelos
próprios instaladores. A skill pessoal chama uma especialidade instalada somente
quando ela atende o trabalho, sem duplicar duas auditorias idênticas por hábito.

## Continuidade, evidência e autoridade

Identifique projeto/issue/executor antes de agir. Retome a tarefa existente e seu
checkpoint; nova tarefa só dentro da autoridade real do aplicativo. Registre revisão,
branch/worktree, dirty state, ambiente, decisões, provas válidas, blockers, próxima
ação, autorizações com alvo/escopo e processos/watcher quando houver.

Evidência reutilizável: alegação, candidato/entradas relevantes, ambiente, fonte ou
comando, horário, resultado, limites e condição de invalidação. Reuse enquanto
compatível; preserve gates finais obrigatórios. Não crie outro ledger, watcher ou
monitor quando os registros do projeto/Gabriel OS já atendem.

Em sessão operacional, respeite recursos próprios, prazo absoluto, orçamento
cumulativo, tentativas, falhas recuperáveis, paradas críticas e cleanup. Preserve
fixtures autorizadas em falhas recuperáveis e a primeira falha sanitizada. Resultado
incerto de mutação deve ser reconciliado antes de retry. Teste defeitos do runner
localmente antes de outra janela ao vivo.

Código pronto, CI verde, staging e produção são estados distintos. Fechamento de
issue depende de seus critérios, não apenas da existência de um commit. Merge,
deploy, publicação, gastos e memória têm autoridade própria. Autorizações válidas
já concedidas não precisam ser pedidas novamente no mesmo escopo. Quando o projeto
exige cleanup pós-merge e já o autoriza, preserve essa exigência e trabalho alheio.

## Medir e melhorar

Use tempo até aceite, retrabalho, espera/intervenções e regressões em tarefas
comparáveis. Não use contagem de skills ou tempo de turno como prova de eficiência.
Aplique `reflect` diante de atrito demonstrado e prefira corrigir a fonte existente
a criar outra camada. Instalação é preparação; piloto real verifica comportamento.

## Ferramentas oficiais via MCP

Quatro procedimentos orientam o uso do Siftr: `gabriel-iss-audit`, `gabriel-github-resolution`, `gabriel-codemap` e `gabriel-improve-codebase-architecture`. Os outros 19 mantêm seus procedimentos. O agente chama `semantic_search`, `focused_read`, `pick_relevant` e, para saída autorizada, `filter_output` experimental pelo MCP oficial. Não há proxy `my-tools search` nesse fluxo.

O my-tools centraliza fonte, SHA aceito, instalação e troca do executável oficial. O MCP deve estar registrado no cliente e conectado na sessão. As skills orientam a escolha antes da primeira busca: localização confirmada → leitura; símbolo exato → rg; comportamento sem localização confirmada → semantic_search. Disponibilidade não garante seleção implícita em todo pedido.

O MCP oficial não usa `.my-tools.json` nem aplica os filtros do launcher legado. Caminhos/dados precisam ser autorizados em cada tarefa; ferramentas nativas não concedem autoridade para envio de conteúdo privado ou dispensam gates. Outro computador ou Cloud precisa de instalação, credencial e configuração próprias.
