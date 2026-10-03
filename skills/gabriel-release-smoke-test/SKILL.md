---
name: gabriel-release-smoke-test
description: "Validar um artefato de release em ambiente limpo, usando o pacote ou build entregue e não o checkout de desenvolvimento."
---

# Smoke do artefato de release

Fase experimental obrigatória: ao ocorrer um gatilho desta skill, execute a ferramenta oficial indicada antes de substituir pela rota habitual. Leia somente a linha pertinente do [roteamento](../../docs/tool-routing.md), que define gatilhos e dispensas. Ler a skill ou consultar `--help` não conta como uso. Registre chamada/resultado ou dispensa concreta no checkpoint existente e resuma isso na entrega; falha da ferramenta pede fallback, não abandono da tarefa.

## Objetivo
Detectar arquivos ausentes, entrypoints quebrados, dependências indevidas do checkout e problemas de configuração no artefato que o consumidor recebe.

1. Identifique tipo de distribuição e candidato: tarball/pacote, binário, container ou build web. Registre origem, revisão, versão e hash quando disponível. Se ainda não há publicação autorizada, use o artefato local exato do candidato.
2. Inspecione empacotamento, scripts de instalação e conteúdo antes de executar. Crie diretório temporário e configuração sintética. Não monte HOME pessoal, agentes SSH, sessões de browser ou credenciais de produção. Um diretório limpo não é sandbox de código não confiável.
3. Instale ou inicie pelo caminho do consumidor, fora do repositório. Confira versão, ajuda/entrypoint, arquivos necessários, bootstrap e caminho mínimo funcional relevante. Para web, sirva o build e confira recursos e fluxo renderizado; para serviço, inicialização e request sintética; para CLI, um comando real além de `--help`.
4. Teste integrações de provedor somente se necessárias, disponíveis e autorizadas. Separe stub, sandbox e provedor real no resultado. Não substitua ausência de credenciais por credenciais pessoais nem invoque APIs pagas por inferência.
5. Verifique mensagens de erro de configuração, desligamento e limpeza de recursos próprios. Preserve o primeiro erro sanitizado. Restrinja smoke às plataformas que consegue testar; não infira Windows/macOS a partir de Linux.
6. Guarde comandos, ambiente, evidência do artefato e resultado. Remova o ambiente temporário próprio quando seguro, preservando evidência não sensível necessária para diagnosticar falha.

## Saída
Artefato/revisão; plataforma; isolamento efetivo; instalação; inicialização; caminho funcional; integrações usadas; cleanup; lacunas. Esta skill não publica nem autoriza deploy.

## Saídas extensas com Jev Pruner
Confirme o wrapper no caminho exato resolvido pela skill do plugin (`<plugin-root>/dist/codex/run.js`), não por `rg --files`, que pode ocultar `dist/`. Registre no checkpoint a causa específica de qualquer fallback; arquivo presente não prova hook/histórico/autorização. A execução exige chamar o wrapper, não apenas carregar a skill.

Para builds, testes ou instalações não interativas que possam gerar logs extensos, consulte a skill do plugin `jev-pruner` antes de executar. É obrigatório executar o comando pelo wrapper original quando o plugin estiver disponível e histórico/saída estiverem autorizados para processamento externo; não executar diretamente apenas por hábito. Saída abaixo do limiar é passthrough válido, não falha nem poda. O My Tools configura OpenRouter com a mesma credencial do Siftr. Não exponha a chave nem a inclua no comando.

Apenas stdout acima de 10 mil tokens estimados pode ser podado. Preserve workdir, argumentos, permissões, checks obrigatórios e critérios de aprovação. Não use para servidores/TTY, leitura de arquivos completos, diffs, dados estruturados ou conteúdo sensível; não aplique também `filter_output` do Siftr ao mesmo resultado. Se faltar runtime, histórico, chave ou rede, execute normalmente e registre a limitação.

O wrapper mantém stderr/exit code e guarda o original no arquivo indicado pelo rodapé. Recupere-o quando faltar contexto. Só registre poda com marcador de omissão; menos texto não prova economia total nem um teste aprovado. Em Cloud, repositórios presentes não substituem instalação, credencial, rede e hook/histórico da sessão.

## Smoke web com Jev Browser

Para validar o build web servido em ambiente limpo, leia a skill upstream `jev-browser-playwright` e execute obrigatoriamente pelo MCP oficial `jev-playwright` ou pela CLI `jev-browser` se o MCP não estiver exposto. Abra sessão isolada sem perfil pessoal, opere o fluxo mínimo e faça assert determinístico do resultado; use `browser_run` apenas quando descoberta semântica ajudar. Confira readback/efeitos e a fonte persistida exigida pelo contrato. Um resultado `unknown` exige reconciliação, não novo envio. Não habilite capacidades extras nem transfira cookies/credenciais pessoais como efeito do smoke. Feche a sessão própria. O My Tools fornece a instalação e a credencial OpenRouter compartilhada; estes testes não substituem evidência visual, gates finais ou autorização de operação real.
