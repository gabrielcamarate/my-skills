# Adoção e ferramentas

Este pacote disponibiliza procedimentos; a instalação não configura infraestrutura,
credenciais, permissões, memória ou ferramentas nos projetos consumidores.

## Base preparada

- Fonte única de 23 procedimentos, com mapa de correspondência ao catálogo de Akita.
- Instalação pessoal por links, com prévia, diagnóstico e desinstalação limitada.
- Regras dos projetos prevalecem; nenhuma migração automática dos seus arquivos.
- Skills de plugins e sistema não são copiadas nem substituídas.

## Aplicação a um projeto

Leia AGENTS/README e a issue atual. Reuse o executor e as provas válidas.
Mapeie scripts de diagnóstico, testes focados, gates finais e smoke existentes.
Só implemente comandos que realmente faltarem, dentro da tarefa autorizada.
Preserve revisão independente, limites operacionais e cleanup já autorizado.
Utilize os registros e mecanismos de acompanhamento do projeto, sem criar outro
monitor por efeito colateral.

Instale as skills no ambiente que executa a tarefa. Um symlink local não conecta
automaticamente outro computador ou ambiente remoto à sua fonte. A descoberta
no runtime escolhido deve ser verificada numa tarefa nova antes de depender dela.

## Ferramentas complementares

Confirme ferramentas disponíveis, versões e acesso antes de usá-las. A documentação
ou a menção a uma ferramenta numa skill não significa que ela está instalada.
Não instale browsers, proxies, programas de painel ou provedores pagos como efeito
colateral de aplicar este pacote. Plugins continuam sob seus próprios instaladores.

AI-Memory é opcional e depende do escopo, política de captura e autorização do
projeto consumidor. Este pacote não cria namespaces, habilita captura ou muda
configuração global. Isolamento de processos também precisa ser verificado:
worktrees e links não isolam rede, credenciais ou execução.

## Critérios para considerar a base operacional

1. Validação e testes do instalador passam.
2. Links apontam para uma única fonte e conflitos preservam dados anteriores.
3. O runtime descobre as skills em uma nova sessão.
4. Uma tarefa piloto demonstra cumprimento dos gates e entrega evidência útil.
5. Tarefas comparáveis permitem medir melhoria; setup não é benchmark de produtividade.

O histórico de verificações locais está em [validation.md](validation.md).
Ele não comprova a instalação de outro usuário nem o funcionamento no Cloud.
