# my-skills

[![Validate skills](https://github.com/gabrielcamarate/my-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/gabrielcamarate/my-skills/actions/workflows/validate.yml)

Skills próprias para Codex e Claude Code. Conteúdo em português brasileiro,
distribuído sob [MIT](LICENSE), com [autoria e créditos](NOTICE.md).

23 procedimentos próprios com correspondência 1:1 aos objetivos do catálogo de
Fabio Akita consultado em 26/09/2026. Adaptados para Gabriel, Codex/Claude e os gates
dos projetos. O [mapa de origem e adaptações](docs/akita-mapping.md) explica cada diferença.

Uma fonte canônica em `skills/`, compartilhada por links individuais. Cada skill
tem um objetivo, descrição de seleção e procedimento próprios. Referências mais
longas são carregadas quando necessárias. Ter 23 skills não significa executar
23 etapas: nomes/descrições têm custo no catálogo e o corpo entra conforme o uso.
Não prometemos economia de tokens apenas por dividir arquivos.

## Catálogo

| Skill | Objetivo |
|---|---|
| `gabriel-agent-browser` | Operar e verificar interfaces no navegador |
| `gabriel-blog-cost-charts` | Comparar qualidade, custo e tempo medidos |
| `gabriel-clonedeps` | Consultar fontes da dependência na versão certa |
| `gabriel-codemap` | Mapear responsabilidades e fluxos do código |
| `gabriel-deepwork` | Coordenar fases complexas com gates claros |
| `gabriel-effect` | Implementar Effect na versão do projeto |
| `gabriel-fact-check` | Conferir fatos, fontes e coerência de textos |
| `gabriel-github-resolution` | Executar correções aprovadas por auditoria |
| `gabriel-humanizer` | Editar linguagem sem inventar fatos ou voz |
| `gabriel-improve-codebase-architecture` | Melhorar fronteiras e contratos de módulos |
| `gabriel-iss-audit` | Investigar issues e decidir a correção |
| `gabriel-loop-engineering` | Executar ciclos com sucesso e parada definidos |
| `gabriel-post-refactor` | Revisar consequências de um refactor |
| `gabriel-pr-audit` | Auditar PRs com evidência do candidato |
| `gabriel-pr-bump` | Atualizar dependências em lotes coerentes |
| `gabriel-pr-post-audit` | Auditar interações entre mudanças do lote |
| `gabriel-reflect` | Melhorar o workflow a partir de atrito real |
| `gabriel-release` | Preparar e verificar releases versionadas |
| `gabriel-release-smoke-test` | Validar o artefato real de uma release |
| `gabriel-security-audit` | Auditar fronteiras e caminhos de ataque |
| `gabriel-simplify` | Simplificar código preservando comportamento |
| `gabriel-verification-planning` | Planejar evidências sem repetir trabalho |
| `gabriel-worktrees` | Gerenciar worktrees sem perder trabalho |

No Codex: `$gabriel-iss-audit`. No Claude Code: `/gabriel-iss-audit`.
Seleção automática permanece disponível conforme a descrição e o runtime.

## Workflow

- Issue: `iss-audit` → decisão autorizada → `github-resolution`.
- PR: `pr-audit` → ajustes autorizados com `github-resolution`.
- Mudança não trivial: `verification-planning` define a prova necessária.
- Mais de três tickets de código no lote: `pr-post-audit` antes de finalizar commit/push.
- Dependências: `pr-bump`; lançamento: `release` com `release-smoke-test`.
- Atrito recorrente: `reflect`; demais skills entram pela necessidade específica.

Os nomes acima usam o prefixo `gabriel-`. Consulte [workflow](docs/workflow.md)
para entrada, saída e limites. Uma pequena edição não exige percorrer essa cadeia.

## Instalação e atualização

Python 3, sem dependências externas no instalador:

```bash
git clone https://github.com/gabrielcamarate/my-skills.git
cd my-skills
python3 scripts/skillctl.py validate
python3 -m unittest discover -s tests -v
python3 scripts/skillctl.py install
python3 scripts/skillctl.py install --apply
python3 scripts/skillctl.py status
```

Sem `--apply`, install/uninstall mostram o plano. `--target codex` ou
`--target claude` limita o consumidor; `--home` permite teste isolado.
Codex usa `~/.agents/skills`; Claude usa `~/.claude/skills`. Não duplicamos a fonte
em `~/.codex/skills` nem substituímos skills de plugins.

Conflitos em destinos ativos abortam antes de criar links. Falha durante instalação
remove somente os links criados nessa tentativa. Após instalar todas as substitutas,
o instalador retira apenas links antigos próprios listados em `skills.json`.
Arquivos, pastas e links de terceiros são preservados, inclusive nos nomes retirados.
Uma falha durante retirada pode deixar alguns links antigos; `status` mostra isso
e uma nova aplicação pode concluir, sem refazer os links válidos.

`status` falha se falta link ativo ou resta link antigo próprio. Um nome antigo
ocupado por terceiros é informado como conflito preservado e não bloqueia as skills
novas. Os quatro nomes aposentados não são aliases; migre prompts conforme o mapa.
O bootstrap está preservado em `archives/bootstrap-2026-09-25/`.

Para desinstalar os links próprios:

```bash
python3 scripts/skillctl.py uninstall
python3 scripts/skillctl.py uninstall --apply
```

Antes de mover o checkout, desinstale, mova e reinstale. Não há atualização remota
automática. Mudanças no upstream são comparadas conscientemente com o commit e
hashes registrados em `docs/upstream-map.json`.

Para atualizar este pacote, com checkout limpo, execute `git pull --ff-only`,
valide e aplique novamente o instalador: links existentes acompanham o conteúdo;
o instalador reconcilia skills adicionadas ou aposentadas sem substituir terceiros.
Quem utiliza este pacote em outro ambiente precisa de um checkout acessível nesse
ambiente. Links do computador pessoal não são sincronizados para o Cloud.

## Manutenção e limites

Edite `skills/<nome>/SKILL.md` e mantenha `skills.json` alinhado. Preserve referências
relativas e metadata em `agents/openai.yaml`. Rode validação e testes após alterar
o instalador. AGENTS/CLAUDE têm paridade; regras privadas continuam nos projetos.

Veja [adoção e ferramentas](docs/adoption.md), [fontes](docs/sources.md),
[cenários de avaliação](docs/evaluation.md) e [evidência local](docs/validation.md).
Instalação disponibiliza procedimentos pessoais; não comprova piloto de entrega,
descoberta em nova sessão ou ganho de produtividade. Ferramentas externas, rollout
nos projetos, publicação no GitHub, produção e captura de memória são escopos distintos.

As skills `gabriel-agent-browser`, `gabriel-verification-planning` e
`gabriel-release-smoke-test` orientam o uso do MCP `jev-playwright` e da skill
upstream `jev-browser-playwright`, quando instalados pelo My Tools. A skill
upstream fica na instalação da ferramenta, fora deste catálogo de 23 skills.
O Chrome pessoal mantém sua própria conexão Jev Browser Control. Veja o
[guia da ferramenta](https://github.com/gabrielcamarate/my-tools/blob/main/docs/jev-browser.md).
