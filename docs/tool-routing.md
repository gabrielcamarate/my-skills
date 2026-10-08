# Uso experimental obrigatório das ferramentas instaladas

Em 03/10/2026 Gabriel autorizou uma fase experimental: **execute a ferramenta oficial
sempre que ocorrer um gatilho compatível abaixo**. Esta é uma regra de execução,
não uma sugestão. Ler a skill, listar capacidades ou executar `--help` não comprova uso.
A regra vale no localhost com as interfaces instaladas; no Cloud depende da preparação
real do ambiente, sem afirmar que publicação no GitHub atualiza sessões abertas.

## Gatilhos e chamadas

| Gatilho observado | Operação obrigatória | Dispensa ou fallback concreto |
|---|---|---|
| Busca por comportamento sem arquivo, trecho ou símbolo confirmado | Siftr `semantic_search`; sem MCP exposto, `siftr search "COMPORTAMENTO" /caminho/autorizado --json --stats` | Localização ou símbolo exato já confirmado: leitura/`rg`; sem interface utilizável ou resultados insuficientes: registrar e buscar diretamente |
| Necessidade de localizar trechos por comportamento dentro de arquivo grande | Siftr `focused_read`, se exposto | Intervalo/termo exato conhecido: leitura delimitada; interface ausente: leitura direta |
| Priorizar lista de arquivos/testes pelo comportamento, sem seleção já conhecida | Siftr `pick_relevant`, se exposto | Seleção já determinada ou interface ausente; gates finais completos |
| Build/teste/instalação não interativos com stdout potencialmente extenso | Wrapper oficial Pruner resolvido pela skill do plugin, antes de executar o comando | TTY/servidor, dados estruturados, leitura/diff, conteúdo ou histórico não autorizado, runtime/histórico/chave indisponível |
| Feedback de iteração de suíte lenta, framework suportado e diff elegível | CLI `jev-test-filter --exec`, com runner/argumentos da skill upstream | Suíte rápida, testes exatos pequenos já definidos, gate final completo, framework incompatível/diff inadequado ou falha de seleção/API |
| Fluxo funcional de navegador em sessão isolada | MCP `jev-playwright` ou CLI oficial `jev-browser`; ler `jev-browser-playwright` | Aba/perfil pessoal indicado, cenário sem suporte, runtime indisponível ou autorização faltante |
| Avaliação de decisões probabilísticas com decisões e rótulos existentes | CLI `jeval ingest`/`report`, conforme skill upstream | Dados/rótulos ausentes ou sem autorização; não criar coleta/instrumentação |

Siftr é a primeira busca semântica; símbolo/mensagem exatos usam `rg`. Use uma pergunta por comportamento. `glob` nesta revisão usa Python fnmatch,
sem expansão de chaves: `{ts,tsx}` exclui arquivos em vez de escolher extensões.
Prefira raiz estreita sem glob, ou CLI `-g "*.ts" -g "*.tsx"`. Se a seleção estiver
vazia por sintaxe de filtro, corrija uma vez; não registre isso como falha do modelo.
Uma pasta presumida não é localização confirmada. Não faça buscas exploratórias sucessivas
para evitar o gatilho. No navegador, seletores conhecidos usam comandos determinísticos
da própria ferramenta; `browser_run` fica para metas que exigem descoberta semântica.
Um script Playwright ad hoc não substitui essa chamada sem motivo concreto. Suites
Playwright já versionadas, RED/GREEN e comparações de pixels são gates independentes;
para o smoke funcional em fixture isolada, use a interface Jev e reutilize prova válida.
QA visual continua exigindo pixels/viewport. Chrome pessoal preserva sua conexão e
conta; não mover cookies/logins para sessão isolada.

Pruner: é obrigatório chamar o wrapper elegível; saída abaixo de 10 mil tokens pode
passar integralmente, e isso é execução válida sem poda. Só alegar poda com marcador
e original recuperável. Não aplicar também `filter_output` do Siftr ao mesmo resultado.
Test Filter seleciona feedback durante iteração; não reduz os checks finais obrigatórios.

Compactação Jev existe só no Claude Code, pelo plugin `fast-jev-compaction` do My Tools
(function hooks `session.compact`, OpenRouter). Ele age sozinho no `/compact` e na
autocompactação; não é skill, MCP nem gatilho para o agente chamar. No Codex não há
esse plugin: o Pruner continua no wrapper e a compactação Jev é só o experimento do
My Tools descrito em `gabriel-reflect`. Só alegar uso com a linha de status
`last /compact: kept N/M messages, no summary`; `fallback to built-in summary` ou o aviso
genérico "Sessão compactada" não provam Jev.

## Exceções, falhas e evidência

Uma dispensa precisa apontar uma condição da tabela ou um conflito real com instrução
superior/projeto, autorização de dados/ações ou capacidade. "Prefiro rg", "considerei",
"não parece necessário" e simples ausência de MCP com CLI disponível não bastam.
Não invente um gatilho para chamar todas as ferramentas; não duplique operações nem
repita uma avaliação cujo candidato/entradas/ambiente permaneçam válidos.

Na primeira operação elegível, confirme a interface uma vez e execute. Falha de
transporte/runtime/contrato: preserve erro sanitizado, registre e continue pela rota
conservadora. Não repetir a mesma falha sem mudança relevante. Resultado incerto de
mutação exige reconciliação somente leitura antes de qualquer reenvio/fallback.
Não reinstalar, mudar hooks/gates, ampliar acesso nem criar outra chave por consequência.
A obrigação não autoriza enviar código privado, conversas, segredos ou dados de clientes.

Use o checkpoint/recibo existente para registrar por tipo de operação:
`gatilho -> chamada/interface -> resultado ou falha -> fallback/dispensa e motivo`.
Na entrega, inclua um resumo curto de ferramentas efetivamente usadas e dispensas
relevantes; não enumere ferramentas sem relação com a tarefa. Distinguir instalação,
chamada, resultado útil e benefício medido. Não fabricar custos/tokens ausentes.

Quando houver baseline comparável, registrar tempo total, contexto/tokens com origem
e unidade, omissões, recuperação e retrabalho. Sem baseline, declarar ganho desconhecido.
Não repetir a tarefa inteira para produzir um benchmark nem ativar coleta automática.
Ajustes futuros devem partir de erros concretos e preservar a primeira evidência.

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
checagem direta antes de perpetuar o fallback. Para coordenação entre chats, use
as ferramentas nativas fornecidas pelo runtime; ausência em uma lista filtrada não
prova que um entrypoint conhecido está indisponível. Verifique a interface e o erro
real uma vez; não trocar ferramenta direta disponível por ponte que exige token
nem inventar APIs. As mensagens continuam limitadas à autorização humana existente.

## Decisão curta no checkpoint existente

Registrar antes da primeira operação elegível de cada tipo, sem repetir por comando:
`necessidade -> ferramenta/interface ou fallback -> evidência/motivo -> resultado`.
Na retomada, reutilizar decisões válidas e rever somente a capacidade que mudou.
Exemplos de motivos específicos: símbolos confirmados para `rg`; poucos testes já
identificados e rápidos para seleção manual; gate final completo para suíte ampla;
histórico privado não autorizado para Pruner. Capturar stdout em arquivo não é poda.

Durante iteração de suíte lenta com diff/framework elegíveis, execute o Test Filter
antes de seleção manual ou execução ampla; use somente as dispensas da tabela.
Gates finais continuam completos. Não inventar uso ou economia para preencher registro.


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

| Ferramenta | Gatilho que exige uso | Operação oficial |
|---|---|---|
| `jev-calibrate` | Avaliar/desenhar perguntas ou limiares com exemplos rotulados e holdout já disponíveis | `jev-calibrate check --provider openrouter`, conforme dataset/skill |
| `jev-axi` | Classificar/ordenar um lote textual com opções/critérios explícitos | `jev-axi pick/rank/triage`, conforme contrato |
| `semdecide` | Aplicar predicado/score/filtro textual a lote ou JSONL com critério definido | CLI `semdecide`, conforme schema |
| `jev-recipes` | Projetar componente de decisões repetitivas em JS/TS | `jev-recipes describe RECEITA`; `run` quando houver entrada válida e piloto autorizado |
| `tocsin` | Triar logs extensos com padrões repetidos | `tocsin triage`; preservar linhas originais |
| `docjev` | Classificar pacote documental em categorias existentes | `docjev classify`; split somente se separação fizer parte do escopo |
| `jev-spec` | Mudança afeta requisitos Markdown/rubricas com configuração já existente | `jev-spec check --format json` |
| `jev-oas-sentinel` | Comparar contratos OpenAPI disponíveis antes/depois de uma mudança | `jev-oas-sentinel compare --base BASE --head HEAD` |
| `hunch` | Revisar diff contra regras explícitas já existentes | `hunch check --base BASE_CONFIRMADA --provider typesafe --no-fallback` |
| `snifftest` | Revisar rascunho com vários parágrafos e regras existentes adequadas ao idioma | CLI `snifftest check`, conforme skill upstream |

Ausência de entrada, categorias, configuração, regras, rótulos ou formato suportado é
dispensa concreta; não criar tais pré-requisitos fora do escopo só para acionar a ferramenta.
Axi e SemDecide são alternativas pelo contrato: escolha uma para o mesmo lote. Recipes
é consulta de componentes, não terceira classificação do mesmo lote. Jeval analisa
decisões registradas; Calibrate avalia perguntas em exemplos rotulados, sem duplicar
uma avaliação equivalente. Hunch não repete a busca do Siftr nesta fase.

Calibrate: `--provider openrouter`. Hunch: `--provider typesafe --no-fallback` usa o transporte OpenRouter adaptado, preservando o nome oficial. Regras/limiares precisam ser apropriados. Spec/Sentinel/Hunch são consultivos; não concedem merge, deploy, aprovação ou gasto. Sniff não reescreve texto nem comprova fatos; DocJev classifica páginas, não verifica alegações.

Siftr continua a primeira rota de busca; Hunch entra para revisão ou alternativa justificada. Axi/Recipes/SemDecide servem contratos distintos: não analisar a mesma lista três vezes. Calibrate precisa de exemplos rotulados e holdout, sem mudar gates automaticamente. Em Cloud, confirmar CLI/runtime, binding e instruções; checkout sozinho não comprova instalação. Nenhuma coleta automática foi habilitada.

## Perfil local e autorização do Pruner

Autorização de processamento depende do operador, fora deste repositório público.
No localhost de Gabriel, consultar a instrução pessoal carregada pelo Codex e, se
necessário, o arquivo `~/.config/my-tools/usage-policy.json`, sem valores de secrets.
O pedido de correção de 03/10/2026 estabelece o perfil para código, fixtures, logs
e histórico comum de sessões técnicas de desenvolvimento autorizadas. Esse perfil
abrange o histórico que o Pruner efetivamente envia, não somente stdout do comando.
Não repetir confirmação por comando em uma sessão inteiramente elegível.

Continuam excluídos: chaves, tokens, credenciais, registros de clientes/financeiros,
logs privados operacionais, mensagens pessoais e sessões com tais conteúdos no
histórico. Presença real desses dados exige dispensa do Pruner nesta sessão, mesmo
se o comando atual for sintético. Não afirmar autorização ausente sem conferir o
perfil e indicar a categoria concreta que impede uso. Não sanear ou substituir o
histórico upstream silenciosamente. O perfil não autoriza produção, deploy, ações
financeiras ou envio de dados de terceiros. Não transportar essa configuração
pessoal pelo Git; Cloud precisa receber sua própria autorização e preparação.

## Guias através dos links instalados

As skills possuem `references/tool-routing.md`, um link interno para o guia único
do repositório. Leia esse arquivo a partir da pasta da skill instalada; não tente
`~/.agents/docs/tool-routing.md`. Outros links relativos de docs devem ser resolvidos
a partir do caminho canônico de SKILL.md (`Path(path).resolve()`), não da pasta
pessoal que contém o link. Não buscar todo o disco após um caminho relativo errado.
