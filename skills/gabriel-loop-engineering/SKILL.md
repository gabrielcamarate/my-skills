---
name: gabriel-loop-engineering
description: "Definir e executar um ciclo limitado de tentativa, verificação e ajuste com condição observável de sucesso e parada."
---

# Ciclo de execução e verificação

Antes de uma operação elegível, siga a [escolha de ferramentas](../../docs/tool-routing.md); registre no checkpoint existente a interface usada ou o motivo concreto do fallback.

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

Para builds, testes ou instalações não interativas que possam gerar logs extensos, consulte a skill do plugin `jev-pruner` antes de executar. Use seu wrapper original quando o plugin estiver disponível e histórico/saída estiverem autorizados para processamento externo. O My Tools configura OpenRouter com a mesma credencial do Siftr. Não exponha a chave nem a inclua no comando.

Apenas stdout acima de 10 mil tokens estimados pode ser podado. Preserve workdir, argumentos, permissões, checks obrigatórios e critérios de aprovação. Não use para servidores/TTY, leitura de arquivos completos, diffs, dados estruturados ou conteúdo sensível; não aplique também `filter_output` do Siftr ao mesmo resultado. Se faltar runtime, histórico, chave ou rede, execute normalmente e registre a limitação.

O wrapper mantém stderr/exit code e guarda o original no arquivo indicado pelo rodapé. Recupere-o quando faltar contexto. Só registre poda com marcador de omissão; menos texto não prova economia total nem um teste aprovado. Em Cloud, repositórios presentes não substituem instalação, credencial, rede e hook/histórico da sessão.

## Seleção de testes na iteração

Quando uma suíte estiver lenta e o diff ainda precisar de feedback durante a implementação, consulte a skill upstream `jev-test-filter` instalada pelo My Tools antes de compor argumentos do runner. Use a CLI oficial com `--exec`: por exemplo, `jev-test-filter --format node --exec -- node --test` para edições locais. Confirme o diff e o framework. Sem `--base`, avalia alterações locais rastreadas contra HEAD. `--base BASE_CONFIRMADA` avalia somente commits entre a merge-base e HEAD; não inclui edições ainda não commitadas. Arquivos novos precisam estar no índice para entrar no diff. Vitest, Jest, Bun, Playwright, Go e Rust têm comandos próprios na skill; pytest não é suportado.

Use somente diff e definições de testes autorizados para envio ao OpenRouter. A mesma `OPENROUTER_API_KEY` é reutilizada, sem copiar a chave por projeto. Se a ferramenta faltar, não houver seleção confiável, o framework for misto ou o diff for ambíguo, execute os testes relevantes diretamente. Falhas de API preservam execução ampla. Seleção probabilística serve ao feedback de iteração; nunca substitui gates finais, CI obrigatório ou a suíte exigida pelo projeto. Registre seleção, falhas e tempo quando houver comparação. Em suítes rápidas, o custo de seleção pode aumentar a duração.

## Confiabilidade de decisões com Jeval

Quando a tarefa envolver avaliar um classificador probabilístico ou uma ferramenta Jev e houver decisões e rótulos autorizados, consulte `jeval-calibration-audit` e, para custos/limiares, `jeval-threshold-from-costs`. Use a CLI gerenciada já instalada: `jeval ingest decisions.jsonl --root /caminho/avaliacao` e `jeval report --root /caminho/avaliacao`. Para logs `jev-native`, ingestão e aplicação dos rótulos são comandos separados conforme a skill/documentação. As seis skills upstream permanecem no My Tools; não rodar curl/main ou outro instalador sobre essa instalação.

Jeval é offline, não requer chave, MCP ou hooks. Avalia decisões produzidas pelas ferramentas que já usam a chave compartilhada OpenRouter. Não instrumentar serviços, coletar logs, mudar gates ou implantar limiares sem escopo próprio. Confirme rótulos gold, amostra, revisão/modelo/pergunta e intervalos; silver é concordância. Sem dados representativos ou runtime, registre a limitação e mantenha a verificação normal. Não atribua redução de tokens ou acurácia geral ao demo ou à instalação.

## Ferramentas opcionais para este escopo

Triagem repetida em lote: avaliar `jev-axi` ou `semdecide`, conforme o contrato. Para avaliar perguntas como filtros, usar `jev-calibrate --provider openrouter` com exemplos rotulados e holdout; não coletar dados ou alterar políticas como efeito colateral. Consulte [roteamento](../../docs/tool-routing.md#decisões-documentos-e-contratos) e o perfil OpenRouter do My Tools. Confirmar disponibilidade nesta sessão e preservar autorização dos dados/gates do projeto.
