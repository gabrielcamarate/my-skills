---
name: gabriel-pr-bump
description: "Consolidar atualizações e alertas de dependências num único PR verificado: lote compatível, piso de supply chain e um passe de CI."
---

# Lote de dependências

Atualizações e alertas viram um único PR. Os comandos vêm do fluxo no `AGENTS.md` do projeto. Exemplo vivo: Xlondz.

1. Liste os PRs do Dependabot (`gh pr list --author app/dependabot`) e os alertas abertos (`gh api repos/O/R/dependabot/alerts`). Classifique cada item: compatível, major ou troca de origem. Major sai do lote e vira issue.
2. **Piso de supply chain:** registry público, nome, versão e checksum conferidos. Fonte git ou path, typosquat ou hook de install novo: pare e faça auditoria completa.
3. **Um lote, um PR, um passe de CI.** Use o gerenciador fixado do projeto (Xlondz: pnpm 10.18.1 em `web/` via `cloud-setup.sh`; `go get` e `go mod tidy` em `wireguard-manager/`). Depois o núcleo rápido (`./scripts/fast-check.sh`), versão e CHANGELOG. Conserte para frente; não serialize.
4. Alerta sem correção upstream: prove se uma mitigação local cobre o advisory (reprodução com e sem ela e teste de regressão) e registre a evidência. A dispensa do alerta fica com Gabriel. Source: xlondz#515, #517.
5. Depois do merge, feche os PRs do Dependabot que ficaram sem objeto e confira se os alertas fecharam.
