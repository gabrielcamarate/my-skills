# Ritual

Uma linha por projeto, no diretório do projeto, como o Akita faz:

> rode gabriel-pr-audit e gabriel-iss-audit, depois gabriel-github-resolution

- Release madura: acrescente "depois gabriel-release".
- Dia de Dependabot: "rode gabriel-pr-bump e gabriel-release".
- Inventário de pendências entre repositórios: `ghpending`.

As skills não carregam comandos de projeto. Cada uma manda seguir o fluxo do `AGENTS.md` do projeto e usa o Xlondz como exemplo vivo (`fast-check`, `cloud-setup`, `integration-ready`, `release cut/check`).

## Regras para escrever ou mudar uma skill

- Procedimento que se repete igual vira skill. Conhecimento vai para `docs/` do projeto ou para o exemplo vivo.
- Cada regra nova traz `Source:` (issue ou PR onde a falha aconteceu). Gosto isolado não vira regra.
- Curta, em passos numerados, sem regra de gerência nem autorização: autorização fica no `settings.json` de cada projeto.
- Skill sem uso em 30 dias é estacionada em `archives/`.

Histórico: o catálogo anterior (23 skills, roteamento obrigatório de ferramentas) está em `archives/skills-parked-2026-10-14/`. A auditoria que motivou a poda está em `Gabriel-OS/drafts/skills-audit-2026-10-14.md`.
- Projeto novo ou fora do padrão: "adote o padrão de projeto com gabriel-project-standard".
