# my-skills

[![Validate skills](https://github.com/gabrielcamarate/my-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/gabrielcamarate/my-skills/actions/workflows/validate.yml)

Skills próprias para Codex e Claude Code. Conteúdo em português brasileiro,
distribuído sob [MIT](LICENSE), com [autoria e créditos](NOTICE.md).

Cinco skills, as do ritual diário do método de Fabio Akita, reescritas a partir das falhas reais dos projetos de Gabriel (14/10/2026). As outras 18 foram estacionadas em `archives/` por falta de uso ou por duplicar o fluxo dos projetos.

## Catálogo

| Skill | Objetivo |
| --- | --- |
| `gabriel-pr-audit` | Parecer sobre um PR: alegações, gates, giro de correções e atribuição |
| `gabriel-iss-audit` | Oráculo, reprodução e menor correção para uma issue |
| `gabriel-github-resolution` | Uma issue de ponta a ponta até a entrega |
| `gabriel-pr-bump` | Lote único de dependências e alertas |
| `gabriel-release` | Versão, publicação e smoke ligados ao SHA exato |

Como usar: [ritual](docs/workflow.md).

## Instalar

**Claude (local e nuvem):** plugin `gabriel` deste repositório, que também é marketplace.

```text
/plugin install gabriel --marketplace gabrielcamarate/my-skills
```

Cada projeto declara o mesmo plugin no `.claude/settings.json` (`extraKnownMarketplaces` e `enabledPlugins`), para que sessões na nuvem carreguem as skills sem copiá-las. No Claude, as skills aparecem como `gabriel:gabriel-pr-audit` etc.

**Codex:** links individuais em `~/.agents/skills`.

```bash
python3 scripts/skillctl.py validate
python3 scripts/skillctl.py install --target codex --apply
```

O `install` também remove os links das skills estacionadas. `--target claude` continua disponível, mas duplica as skills se o plugin estiver ativo.
