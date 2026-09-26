---
name: gabriel-worktrees
description: "Criar, inspecionar ou limpar worktrees Git para isolamento justificado, preservando branches ativas, alterações locais e arquivos ignorados."
---

# Worktrees

## Objetivo
Separar arquivos e branches de trabalho quando houver necessidade de isolamento. Worktree não isola credenciais, rede ou execução maliciosa.

1. Identifique repositório, revisão de partida, branch, caminho, dirty state e `git worktree list`. Confirme se já existe executor/checkpoint da mesma issue e reutilize-o quando possível. Não crie uma nova tarefa de aplicativo sem pedido explícito.
2. Prefira o mecanismo gerenciado do runtime quando disponível e adequado. No Codex, use prefixo `codex/` salvo convenção explícita diferente. Registre o caminho retornado e use-o em comandos seguintes; a criação não muda automaticamente o cwd.
3. Preserve alterações não commitadas: elas não são copiadas automaticamente para um novo worktree. Não faça reset/stash/clean indiscriminado para obter checkout limpo. Verifique colisões locais/remotas antes de criar branch.
4. Leia instruções e gates do checkout de destino. Em projetos com captura controlada, verifique o próprio marcador, escopo e política antes de trabalho substantivo. Não copie marcador de outro projeto nem repare captura sem autorização.
5. Mantenha ownership de arquivos e artefatos de teste na lane correta. Integração/rebase/merge seguem autoridade e política do projeto, com revisão do candidato resultante.
6. Para limpeza autorizada, atualize refs e confirme PR/head integrado, ausência de commits posteriores, inexistência de PR aberto e inatividade do worktree. Squash exige evidência do PR/head e da integração, não ancestralidade isolada.
7. Inspecione arquivos tracked, untracked e ignorados antes de remover. Preserve main, branches avançadas/não integradas, worktrees locked/ativas/dirty e quaisquer arquivos de usuário ou segredos. Nunca force remoção para fazer cleanup parecer concluído. Se o executor não pode remover seu próprio checkout, a coordenação conclui após ele parar.

## Saída
Inventário final de branches/worktrees, alterações executadas e itens preservados com motivo. No Xlondz, aplique a autorização de cleanup pós-merge já existente sem pedi-la de novo; ela não autoriza o merge.
