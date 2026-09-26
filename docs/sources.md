# Fontes e decisões de adaptação

Consultadas em 25/09/2026. Procedimentos escritos para Gabriel, inspirados na pesquisa
do AI Lair e nas instruções atuais do Gabriel OS. Sem cópia integral do pacote alheio.

- [AI Lair: workflow](https://ailair.akitaonrails.com/pt-br/workflow/): continuidade e procedimentos recorrentes.
- [Akita: skills](https://akitaonrails.com/2026/09/17/falando-um-pouco-sobre-minhas-skills-de-ia/): adaptar às próprias restrições.
- [my-skills do Akita](https://github.com/akitaonrails/my-skills): auditoria de alegações, resolução, verificação e release.
- [OpenAI: skills](https://learn.chatgpt.com/docs/build-skills): formato, descoberta em ~/.agents/skills e symlinks.
- [Claude Code: skills](https://code.claude.com/docs/en/skills): descoberta pessoal em ~/.claude/skills e symlinks.
- [AI-Memory: workstreams](https://github.com/akitaonrails/ai-memory/blob/HEAD/docs/managed-workstreams.md): continuidade e efeitos de autowire.
- [AI-Memory: autoaperfeiçoamento](https://github.com/akitaonrails/ai-memory/blob/HEAD/docs/auto-improvement-loop.md): aprovação de propostas é uma política separada.

## Escolhas do bootstrap em 25/09/2026 (histórico)

- O bootstrap começou com seis capacidades. Essa limitação foi substituída em 26/09/2026 pela correspondência de 23 objetivos documentada abaixo.
- Prefixo gabriel- evita colisão com audit, release e verify de outros fornecedores.
- Fonte única por symlinks; sem converter diretórios gerenciados em links.
- Nenhum deploy implícito, callback de OpenCode, comando Rails ou caminho pessoal de Akita.
- Sem cópia das skills específicas do Gabriel OS, que dependem dos arquivos daquele projeto.
- Sem hook automático, provedor de LLM, MCP adicional ou gravação de memória.

As fontes explicam o raciocínio. Não são prova de que este pacote melhora velocidade
ou de que todo comportamento foi reproduzido nos dois aplicativos.


## Correspondência integral do catálogo em 26/09/2026

Referência fixada: `akitaonrails/my-skills` no commit
`285ca8275a3c61ee856deb7a55db21de3f62526d`. O mapa detalhado de 23 objetivos,
URLs individuais, hashes dos SKILL.md consultados e diferenças deliberadas está em
[akita-mapping.md](akita-mapping.md) e [upstream-map.json](upstream-map.json).

O texto local é uma adaptação própria. Scripts e arquivos auxiliares do upstream
não foram vendorizados, nem foi presumida uma licença geral para o repositório.
A separação e os procedimentos preservam o modelo do autor; permissões, runtime,
voz, plataformas e condições de aceite seguem nossa realidade e estão discriminados.
