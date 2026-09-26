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

## Escolhas locais

- Seis capacidades independentes em vez de instalar as 23 skills examinadas.
- Prefixo gabriel- evita colisão com audit, release e verify de outros fornecedores.
- Fonte única por symlinks; sem converter diretórios gerenciados em links.
- Nenhum deploy implícito, callback de OpenCode, comando Rails ou caminho pessoal de Akita.
- Sem cópia das skills específicas do Gabriel OS, que dependem dos arquivos daquele projeto.
- Sem hook automático, provedor de LLM, MCP adicional ou gravação de memória.

As fontes explicam o raciocínio. Não são prova de que este pacote melhora velocidade
ou de que todo comportamento foi reproduzido nos dois aplicativos.
