# my-skills

Skills próprias de Gabriel para entregar software com continuidade e evidência.
Uma fonte em `skills/`, compartilhada por links individuais com Codex e Claude Code.
O conteúdo é uma adaptação própria; não é um clone do pacote pessoal do Akita.

## Uso

| Necessidade | Skill |
|---|---|
| Entender uma issue e definir o que comprova a correção | `gabriel-triage` |
| Revisar um PR ou diff | `gabriel-pr-review` |
| Implementar uma issue autorizada | `gabriel-resolve` |
| Definir ou reconciliar evidências de aceite | `gabriel-verify` |
| Preparar ou executar uma release autorizada | `gabriel-release` |
| Melhorar um procedimento a partir de atrito real | `gabriel-reflect` |

No Codex, invoque `$gabriel-triage`; no Claude Code, `/gabriel-triage`.
Também podem ser selecionadas pelo agente quando a descrição corresponder ao pedido.
As fases são capacidades independentes, não uma cadeia obrigatória para toda edição.
Exemplo: “Use gabriel-triage na issue indicada e resolva o escopo autorizado com
gabriel-resolve. Preserve os gates do projeto e apresente a evidência final.”

## Instalação local

Execute da raiz deste repositório, com Python 3:

```bash
python3 scripts/skillctl.py validate
python3 -m unittest discover -s tests -v
python3 scripts/skillctl.py install
python3 scripts/skillctl.py install --apply
python3 scripts/skillctl.py status
```

Sem `--apply`, install/uninstall mostram apenas o plano. `--target codex` ou
`--target claude` limita o destino. `status` retorna erro se faltar algum link.
Codex usa `~/.agents/skills`; Claude usa `~/.claude/skills`. Não criamos uma segunda
cópia em `~/.codex/skills`. Conflitos abortam a instalação antes de criar links.
O instalador nunca substitui conteúdo existente. Uma falha durante a aplicação
remove somente os links criados naquela tentativa; diretórios vazios podem permanecer.

Para desinstalar:

```bash
python3 scripts/skillctl.py uninstall
python3 scripts/skillctl.py uninstall --apply
```

Somente symlinks que ainda apontam para esta fonte são removidos. Arquivos, diretórios
e links redirecionados a outras fontes são preservados. Para mover o checkout,
desinstale seus links antes, mova e reinstale. Não há atualização automática por rede.

## Manutenção

Edite `skills/<nome>/SKILL.md` aqui. Valide o inventário e teste o instalador.
Novas skills entram explicitamente em `skills.json`. Para retirar uma skill,
desinstale antes de remover sua entrada do inventário e reinstale as restantes.
Skills de projeto ficam no projeto; plugins continuam sob seu gerenciador.
As skills locais do Gabriel OS continuam no fluxo de manutenção próprio dele.

Veja [workflow](docs/workflow.md), [adoção e ferramentas](docs/adoption.md),
[fontes](docs/sources.md) e [cenários de avaliação](docs/evaluation.md).

Este repositório não contém chaves, modelos, MCPs, hooks, automações ou configuração
de AI-Memory. Não registra namespace nem altera captura. Sua instalação disponibiliza
procedimentos pessoais, mas não altera código, gates ou autoridade dos projetos.
Publicação no GitHub e implantação nos projetos são etapas separadas.

Links e validação estrutural não provam desempenho do agente. Confira a descoberta
em uma nova sessão de cada aplicativo e avalie o uso em tarefas reais antes de
afirmar ganho de produtividade.
