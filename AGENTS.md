# Gabriel Skills

Repositório de procedimentos reutilizáveis de Gabriel. A fonte canônica é skills/.

- Leia README.md para operação e docs/workflow.md para os limites entre fases.
- Edite skills aqui; o instalador cria links individuais, sem copiar ou substituir diretórios de plugins.
- Preserve instruções e gates do projeto de destino. Uma skill não concede autorização operacional.
- Mantenha descrições curtas e específicas. Não acrescente dependências de outro agente ou ferramentas indisponíveis.
- Scripts locais usam Python 3 e biblioteca padrão. Valide com python3 scripts/skillctl.py validate e python3 -m unittest discover -s tests -v.
- AGENTS.md e CLAUDE.md compartilham este conteúdo; atualize ambos juntos.
- Não inclua credenciais, logs privados, checkpoints de clientes ou configuração pessoal. Não habilite captura de AI-Memory neste repositório sem autorização própria e namespace registrado.
- Publicação remota, instalação de outros programas e alterações nos projetos consumidores são etapas separadas. Não presuma autorização a partir de uma edição de skill.

- Preserve um objetivo reconhecível por skill e descrições de seleção distintas. Vários passos para o mesmo resultado não exigem várias skills. Não carregue o catálogo inteiro para executar uma fase.
- Mantenha docs/akita-mapping.md e docs/upstream-map.json como registro de procedência e adaptações; atualizar upstream exige comparação, não cópia automática.
