# Revisão estática e evidência

## Antes de executar código de terceiros

Leia cada hunk e os arredores necessários. Confira modos executáveis, symlinks,
submódulos, binários, código gerado, controles Unicode e dados codificados sem
explicação. Em arquivos grandes ou gerados, registre o método e as limitações da
inspeção; não diga “diff inteiro revisado” se houve truncamento.

Manifests, lockfiles, configuração de package manager, hooks, filtros Git,
Dockerfiles, workflows e setup de testes são superfícies executáveis. Examine
registry inesperado, git/path dependency, pacote parecido com outro, integridade,
lifecycle scripts, plugins de compilação e backend de build. Testes e exemplos
podem executar antes da primeira assertiva.

Em CI, confira permissões de escrita, `pull_request_target`, segredos expostos a
código não confiável, interpolação em shell, substituição de artefatos e ações
sem versão imutável. Check verde perde valor se o próprio PR removeu o teste.

Trace acessos a credenciais/ambiente, rede/telemetria, processos, filesystem,
carregamento dinâmico, desserialização, queries, templates e extração de arquivos.
Comportamento suspeito sem explicação bloqueia execução. Documente a evidência
sem imprimir segredos e sem rodar o payload “para ver o que acontece”.

## Execução e isolamento

Inspecione hooks e filtros antes de checkout. Escolha container/VM/sandbox com
isolamento real quando a confiança exigir; worktree sozinho não faz isso.
Não exponha HOME, agentes SSH, cloud metadata, Docker socket, browser pessoal ou
credenciais de produção. Limite rede quando possível e registre risco residual.
Sem isolamento adequado, conclua a revisão estática e marque testes não rodados.

## Validade das provas

Associe cada resultado a commit/árvore, entradas, lockfile, toolchain, configuração,
ambiente, comando e execução. Resultado anterior só cobre arquivos e condições
relevantes equivalentes. Um ajuste de prosa pode preservar prova de runtime; uma
mudança em build, fixture, schema, dependência ou workflow pode invalidá-la.

Rode checks focados durante ajustes e o gate obrigatório no candidato final.
Um novo head exige revisar o delta, não repetir automaticamente tudo. Uma alteração
de versão exige validar resolução de metadados e pacote/build afetado. Não dispense
gates que as instruções confiáveis vinculam explicitamente ao SHA final.

CI pending, cancelado ou skipped não é PASS. Execução de PR e execução após merge
podem testar composições diferentes. Confira a base e o SHA exatos antes de alegar
integração validada. Não cancele jobs remotos sem autoridade para essa operação.

## Parecer

Separe falha crítica de segurança, bloqueio de correção/compatibilidade/prova,
melhoria recomendada e detalhe cosmético. Incerteza de valor pede investigação
delimitada; incerteza de segurança não deve virar aprovação. Cada achado precisa
de cenário concreto, evidência, efeito e correção proporcional.
