---
name: gabriel-verification-planning
description: "Definir ou reconciliar a evidência necessária para provar uma mudança não trivial, incluindo validade de verificações anteriores."
---

# Planejamento de verificação

Antes de uma operação elegível, siga a [escolha de ferramentas](../../docs/tool-routing.md); registre no checkpoint existente a interface usada ou o motivo concreto do fallback.

## Objetivo
Transformar uma alegação de entrega em evidência observável com custo proporcional. Não é uma suite universal de testes.

1. Expresse a alegação, entradas, ambiente, fronteiras e invariantes que devem permanecer. Identifique o erro mais importante que um falso PASS esconderia.
2. Inventarie evidência existente: revisão, arquivos/entradas relevantes, configuração, ambiente, horário, resultado e limitações. Reutilize somente enquanto essas condições continuarem válidas e as regras do projeto permitirem. Gate obrigatório do head final permanece obrigatório.
3. Compare caminhos possíveis: teste de lógica, integração, inspeção de artefato, UI renderizada, estado remoto ou medição operacional. Escolha o caminho mais barato que realmente diferencia sucesso de falha. Um build não prova comportamento visual; um usuário não prova cinco simultâneos.
4. Atribua uma fonte responsável por cada alegação e evite verificações duplicadas. Defina critério de aprovação, resultado inconclusivo, invalidação e orçamento de execução. Para operação real, explicite ambiente, recursos próprios, expiração, custos/tráfego, tentativas, falhas recuperáveis, paradas críticas e limpeza.
5. Se falta observabilidade, escolha a menor instrumentação necessária e seu ciclo de vida. Aproveite fixtures e ferramentas existentes. Mudanças estruturais, persistência ou dependências fora do escopo não são consequência automática de querer evidência.
6. Torne o caminho reproduzível. Registre comandos confiáveis e parâmetros não sensíveis. Preserve a primeira falha antes de limpeza. Teste localmente defeitos do runner antes de pedir outra janela remota.
7. Interprete os resultados contra a alegação: estabelecida, limitada ou refutada. Diferencie falha da medição, falha do produto e falha de cleanup. Apresente a próxima evidência que resolve uma lacuna.

## Saída
Use o registro existente da tarefa: alegação → fonte/comando → candidato e ambiente → resultado → limites/invalidação. Não crie um segundo ledger ou monitor quando o projeto já possui um.

## Saídas extensas com Jev Pruner
Para builds, testes ou instalações não interativas que possam gerar logs extensos, consulte a skill do plugin `jev-pruner` antes de executar. Use seu wrapper original quando o plugin estiver disponível e histórico/saída estiverem autorizados para processamento externo. O My Tools configura OpenRouter com a mesma credencial do Siftr. Não exponha a chave nem a inclua no comando.

Apenas stdout acima de 10 mil tokens estimados pode ser podado. Preserve workdir, argumentos, permissões, checks obrigatórios e critérios de aprovação. Não use para servidores/TTY, leitura de arquivos completos, diffs, dados estruturados ou conteúdo sensível; não aplique também `filter_output` do Siftr ao mesmo resultado. Se faltar runtime, histórico, chave ou rede, execute normalmente e registre a limitação.

O wrapper mantém stderr/exit code e guarda o original no arquivo indicado pelo rodapé. Recupere-o quando faltar contexto. Só registre poda com marcador de omissão; menos texto não prova economia total nem um teste aprovado. Em Cloud, repositórios presentes não substituem instalação, credencial, rede e hook/histórico da sessão.

## Seleção de testes na iteração

Quando uma suíte estiver lenta e o diff ainda precisar de feedback durante a implementação, consulte a skill upstream `jev-test-filter` instalada pelo My Tools antes de compor argumentos do runner. Use a CLI oficial com `--exec`: por exemplo, `jev-test-filter --format node --exec -- node --test` para edições locais. Confirme o diff e o framework. Sem `--base`, avalia alterações locais rastreadas contra HEAD. `--base BASE_CONFIRMADA` avalia somente commits entre a merge-base e HEAD; não inclui edições ainda não commitadas. Arquivos novos precisam estar no índice para entrar no diff. Vitest, Jest, Bun, Playwright, Go e Rust têm comandos próprios na skill; pytest não é suportado.

Use somente diff e definições de testes autorizados para envio ao OpenRouter. A mesma `OPENROUTER_API_KEY` é reutilizada, sem copiar a chave por projeto. Se a ferramenta faltar, não houver seleção confiável, o framework for misto ou o diff for ambíguo, execute os testes relevantes diretamente. Falhas de API preservam execução ampla. Seleção probabilística serve ao feedback de iteração; nunca substitui gates finais, CI obrigatório ou a suíte exigida pelo projeto. Registre seleção, falhas e tempo quando houver comparação. Em suítes rápidas, o custo de seleção pode aumentar a duração.

## Evidência funcional com Jev Browser

Para fluxos funcionais de navegador em sessões Playwright isoladas, consulte `jev-browser-playwright` quando o MCP `jev-playwright` estiver disponível. Planeje uma meta limitada com `browser_run`, seguida do assert determinístico pertinente e da checagem persistida quando exigida. Se os alvos forem conhecidos, comandos nativos evitam inferência e sua latência. `complete` depende de evidência: confira `verification.readback`, `unobserved` e efeitos; nunca repita gravação `unknown` sem reconciliação. Avaliação visual requer imagem/renderização, não apenas DOM ou julgamento Jev. Preserve gates do projeto, autorização de dados/ações e fallback para a ferramenta já disponível. A skill upstream permanece na instalação My Tools.
