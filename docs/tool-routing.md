# Escolha das ferramentas instaladas

Antes da primeira operação elegível, escolha pela necessidade e capacidades desta sessão.
Não repita discovery a cada comando nem carregue todo o catálogo. Use o registro existente
para anotar ferramenta/interface e resultado; em fallback elegível, anote um motivo concreto.
Instalação, disponibilidade, chamada executada e benefício medido são estados distintos.

| Necessidade | Rota |
|---|---|
| Arquivo já confirmado / identificador exato | Leitura direta / `rg`, sem inferência |
| Comportamento sem localização confirmada | Siftr `semantic_search`, se conectado e envio autorizado |
| Feedback de uma suíte lenta durante iteração | Skill upstream `jev-test-filter` e CLI; gates finais continuam completos |
| stdout potencialmente extenso, não interativo | Skill `jev-pruner` e wrapper, se histórico inteiro e saída autorizados; exigir marcador antes de alegar poda |
| Fluxo funcional em navegador isolado | Preferir `jev-playwright` ou CLI `jev-browser`; comandos nativos para alvos conhecidos, `browser_run` para metas adequadas |
| Aba/perfil pessoal indicado pelo usuário | Preservar a conexão e conta existentes; não migrar cookies para navegador isolado |
| Medir confiança/erros de decisões probabilísticas rotuladas | CLI `jeval` e skill upstream `jeval-calibration-audit`; offline, sem hooks/MCP; não implanta políticas |
| QA visual | Usar superfície que exponha pixels e viewport necessária; Jev screen quando disponível, ou CUA/capacidade visual adequada |

Fallback: capacidade ausente/falhou, cenário incompatível, dados não autorizados ou rota
nativa mais adequada ao critério. Não trocar silenciosamente uma rota elegível por hábito,
nem chamar o modelo apenas para demonstrar uso. Reconcilie mutação incerta antes de trocar
ferramenta; preserve gates, ownership e cleanup. Não instale/configure clientes por efeito
colateral. Sessões antigas podem manter um catálogo anterior: verificar disponibilidade
real uma vez. Links locais não configuram automaticamente MCPs, plugins ou Cloud.

## Descoberta verificável, uma vez por sessão

Resolver o entrypoint pela skill instalada ou pelo registro do My Tools. Para um
arquivo conhecido, conferir o caminho exato com `test -f`/`test -r` ou `Path.is_file()`;
para uma CLI, usar `command -v` e seu `--help` quando necessário. `rg --files` respeita
ignores e pode esconder `dist/`: resultado vazio não comprova que o wrapper falta.
Não buscar todo o disco, instalar novamente ou executar uma chamada paga apenas
para confirmar que um arquivo existe. Reusar a descoberta até mudar instalação,
runtime, conexão ou ocorrer falha concreta.

No Pruner, resolver a raiz segundo a skill do plugin e conferir
`<plugin-root>/dist/codex/run.js` diretamente. A presença do arquivo não comprova
hook confiado, histórico disponível, autorização de envio ou poda. Plugin/hook não
envolve comandos automaticamente: o agente precisa chamar o wrapper oficial.
Distinguir `arquivo ausente`, `runtime ausente`, `histórico indisponível`,
`dados não autorizados` e `comando inelegível`; não resumir tudo como indisponível.
Se a descoberta anterior usou uma listagem filtrada, corrigir o checkpoint pela
checagem direta antes de perpetuar o fallback.

## Decisão curta no checkpoint existente

Registrar antes da primeira operação elegível de cada tipo, sem repetir por comando:
`necessidade -> ferramenta/interface ou fallback -> evidência/motivo -> resultado`.
Na retomada, reutilizar decisões válidas e rever somente a capacidade que mudou.
Exemplos de motivos específicos: símbolos confirmados para `rg`; poucos testes já
identificados e rápidos para seleção manual; gate final completo para suíte ampla;
histórico privado não autorizado para Pruner. Capturar stdout em arquivo não é poda.

Durante iteração de suíte lenta, avaliar explicitamente o Test Filter antes de
substituí-lo por seleção manual ou execução ampla. Se o critério já tem um conjunto
pequeno e conhecido de testes, registrar essa escolha e executar diretamente.
Gates finais continuam completos. Não exigir todas as ferramentas em toda tarefa,
nem inventar uso, economia ou indisponibilidade para preencher o registro.


## Pré-requisitos de autenticação

Quando QA depender de identidade sintética/MFA, resolver a fonte no runbook do
projeto durante o preflight inicial. Ausência no env da worktree não prova ausência
no host; configuração de CI não fica automaticamente disponível localmente.
Procurar somente os locators documentados, conferir política de captura e carregar
segredos somente em memória autorizada. Registrar presença/validação/bloqueio sem
valores. Sem fonte, delimitar a lacuna; não exportar secrets de CI, contornar MFA,
rotacionar fatores ou copiar credenciais para cada checkout por conta própria.



## Decisões, documentos e contratos

Usar o perfil OpenRouter do [My Tools](https://github.com/gabrielcamarate/my-tools/blob/main/docs/reviewed-tools.md), com chave compartilhada fora do repositório. Não usar instaladores flutuantes das skills nem criar chaves por projeto.

| Ferramenta | Necessidade |
|---|---|
| `jev-calibrate` | Avalia perguntas e limiares com exemplos rotulados |
| `jev-axi` | Classifica e ordena decisões em lote |
| `jev-recipes` | 248 decisões tipadas para automações e aplicações |
| `tocsin` | Agrupa e prioriza padrões de logs |
| `docjev` | Classifica documentos e separa páginas |
| `jev-spec` | Compara código com requisitos Markdown |
| `jev-oas-sentinel` | Detecta riscos de incompatibilidade OpenAPI |
| `hunch` | Busca comportamento e revisa diffs contra regras |
| `snifftest` | Verifica texto contra regras de estilo |
| `semdecide` | Classifica e filtra texto ou JSONL |

Calibrate: `--provider openrouter`. Hunch: `--provider typesafe --no-fallback` usa o transporte OpenRouter adaptado, preservando o nome oficial. Regras/limiares precisam ser apropriados. Spec/Sentinel/Hunch são consultivos; não concedem merge, deploy, aprovação ou gasto. Sniff não reescreve texto nem comprova fatos; DocJev classifica páginas, não verifica alegações.

Siftr continua a primeira rota de busca; Hunch entra para revisão ou alternativa justificada. Axi/Recipes/SemDecide servem contratos distintos: não analisar a mesma lista três vezes. Calibrate precisa de exemplos rotulados e holdout, sem mudar gates automaticamente. Em Cloud, confirmar CLI/runtime, binding e instruções; checkout sozinho não comprova instalação. Nenhuma coleta automática foi habilitada.
