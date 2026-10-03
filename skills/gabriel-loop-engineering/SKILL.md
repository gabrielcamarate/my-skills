---
name: gabriel-loop-engineering
description: "Definir e executar um ciclo limitado de tentativa, verificação e ajuste com condição observável de sucesso e parada."
---

# Ciclo de execução e verificação

Fase experimental obrigatória: ao ocorrer um gatilho desta skill, execute a ferramenta oficial indicada antes de substituir pela rota habitual. Leia somente a linha pertinente do [roteamento](../../docs/tool-routing.md), que define gatilhos e dispensas. Ler a skill ou consultar `--help` não conta como uso. Registre chamada/resultado ou dispensa concreta no checkpoint existente e resuma isso na entrega; falha da ferramenta pede fallback, não abandono da tarefa.

Para implementação não trivial, siga o [feedback antecipado](../../docs/fast-feedback.md): pré-requisitos e integração real cedo, testes em execução única, reuso de CI válido e preflight documental do projeto antes de publicação. Preserve gates e autoridade.

1. Extraia do pedido objetivo, critério observável, executor e verificador. Pergunte apenas pelo que realmente falta; não reinicie uma entrevista se as respostas estão no contexto.
2. Defina sucesso por teste, build, comando, arquivo/artefato, observação ou revisão humana. Existência de arquivo só basta quando é o critério real; arquivo vazio não comprova comportamento. Registre comando/fonte e interpretação.
3. Fixe tentativas, prazo e orçamento. Para iteração local reversível, três tentativas é um limite inicial útil; autorização mais estreita prevalece. Operação real exige limites de recursos, custo, reconciliação e cleanup já acordados. Não reinicie a contagem entre fases.
4. Execute uma tentativa, guarde o primeiro erro sanitizado e classifique a falha. Ajuste só a hipótese sustentada pelos dados. Reutilize recursos compatíveis dentro da sessão autorizada; não destrua fixtures automaticamente após falha recuperável.
5. Pare em sucesso comprovado, cancelamento, limite, perda de ownership/contabilidade, falha crítica ou decisão humana necessária. Resultado desconhecido de mutação precisa ser reconciliado antes de repetir.
6. Use callbacks somente se o runtime os oferece. Caso contrário, acompanhe os processos/ferramentas reais com esperas limitadas e checkpoint. Não invoque APIs fictícias `onLoopComplete` ou `resolveManualReview`. Verificação humana permanece pendente até resposta; tempo decorrido não é aprovação.

## Entrega
Tentativas e evidências, hipótese atual, resultado, recursos retidos/limpos e próxima ação. Não converta “continuar tentando” em gasto ilimitado, retry automático ou nova autorização.

## Saídas extensas com Jev Pruner
Confirme o wrapper no caminho exato resolvido pela skill do plugin (`<plugin-root>/dist/codex/run.js`), não por `rg --files`, que pode ocultar `dist/`. Registre no checkpoint a causa específica de qualquer fallback; arquivo presente não prova hook/histórico/autorização. A execução exige chamar o wrapper, não apenas carregar a skill.

Para builds, testes ou instalações não interativas que possam gerar logs extensos, consulte a skill do plugin `jev-pruner` antes de executar. É obrigatório executar o comando pelo wrapper original quando o plugin estiver disponível e histórico/saída estiverem autorizados para processamento externo; não executar diretamente apenas por hábito. Saída abaixo do limiar é passthrough válido, não falha nem poda. O My Tools configura OpenRouter com a mesma credencial do Siftr. Não exponha a chave nem a inclua no comando.

Apenas stdout acima de 10 mil tokens estimados pode ser podado. Preserve workdir, argumentos, permissões, checks obrigatórios e critérios de aprovação. Não use para servidores/TTY, leitura de arquivos completos, diffs, dados estruturados ou conteúdo sensível; não aplique também `filter_output` do Siftr ao mesmo resultado. Se faltar runtime, histórico, chave ou rede, execute normalmente e registre a limitação.

O wrapper mantém stderr/exit code e guarda o original no arquivo indicado pelo rodapé. Recupere-o quando faltar contexto. Só registre poda com marcador de omissão; menos texto não prova economia total nem um teste aprovado. Em Cloud, repositórios presentes não substituem instalação, credencial, rede e hook/histórico da sessão.

## Seleção de testes na iteração

Quando uma suíte estiver lenta e o diff ainda precisar de feedback durante a implementação, consulte a skill upstream `jev-test-filter` instalada pelo My Tools antes de compor argumentos do runner. Nesse cenário, é obrigatório executar a CLI oficial com `--exec`, antes de escolher testes manualmente ou repetir a suíte inteira: por exemplo, `jev-test-filter --format node --exec -- node --test` para edições locais. Confirme o diff e o framework. Sem `--base`, avalia alterações locais rastreadas contra HEAD. `--base BASE_CONFIRMADA` avalia somente commits entre a merge-base e HEAD; não inclui edições ainda não commitadas. Arquivos novos precisam estar no índice para entrar no diff. Vitest, Jest, Bun, Playwright, Go e Rust têm comandos próprios na skill; pytest não é suportado.

Use somente diff e definições de testes autorizados para envio ao OpenRouter. A mesma `OPENROUTER_API_KEY` é reutilizada, sem copiar a chave por projeto. Se a ferramenta faltar, não houver seleção confiável, o framework for misto ou o diff for ambíguo, execute os testes relevantes diretamente. Falhas de API preservam execução ampla. Seleção probabilística serve ao feedback de iteração; nunca substitui gates finais, CI obrigatório ou a suíte exigida pelo projeto. Registre seleção, falhas e tempo quando houver comparação. Em suítes rápidas, o custo de seleção pode aumentar a duração.

## Confiabilidade de decisões com Jeval

Quando a tarefa envolver avaliar um classificador probabilístico ou uma ferramenta Jev e houver decisões e rótulos autorizados, consulte `jeval-calibration-audit` e, para custos/limiares, `jeval-threshold-from-costs`. Nesse cenário, execute obrigatoriamente a CLI gerenciada já instalada: `jeval ingest decisions.jsonl --root /caminho/avaliacao` e `jeval report --root /caminho/avaliacao`. Para logs `jev-native`, ingestão e aplicação dos rótulos são comandos separados conforme a skill/documentação. As seis skills upstream permanecem no My Tools; não rodar curl/main ou outro instalador sobre essa instalação.

Jeval é offline, não requer chave, MCP ou hooks. Avalia decisões produzidas pelas ferramentas que já usam a chave compartilhada OpenRouter. Não instrumentar serviços, coletar logs, mudar gates ou implantar limiares sem escopo próprio. Confirme rótulos gold, amostra, revisão/modelo/pergunta e intervalos; silver é concordância. Sem dados representativos ou runtime, registre a limitação e mantenha a verificação normal. Não atribua redução de tokens ou acurácia geral ao demo ou à instalação.

## Ferramentas obrigatórias nos gatilhos deste escopo

Em triagem textual em lote, use `jev-axi` para escolha/ranking ou `semdecide` para predicados/texto/JSONL; escolha uma interface pelo contrato, sem processar o mesmo lote duas vezes. Ao avaliar perguntas de decisão com exemplos rotulados disponíveis, use `jev-calibrate --provider openrouter`. Não coletar dados ou alterar políticas por consequência. Veja [gatilhos e dispensas](../../docs/tool-routing.md#decisões-documentos-e-contratos).
