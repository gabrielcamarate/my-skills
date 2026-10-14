---
name: gabriel-release-smoke-test
description: "Validar um artefato de release em ambiente limpo, usando o pacote ou build entregue e não o checkout de desenvolvimento."
---

# Smoke do artefato de release

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
