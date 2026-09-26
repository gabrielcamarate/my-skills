# Adoção e ferramentas

Preparação local em 25/09/2026. Xlondz é o primeiro candidato à aplicação porque Gabriel
prioriza concluir o produto e receber clientes. Rakmma mantém sua rota própria.
Low Ticket foi retirado do escopo pelo usuário.

## Base preparada

- Fonte única de seis procedimentos portáveis.
- Instalação pessoal por links, com prévia, diagnóstico e desinstalação limitada.
- Regras dos projetos prevalecem; nenhuma migração dos seus arquivos nesta etapa.
- Skills de plugins e sistema não são copiadas nem substituídas.

## Aplicação posterior ao Xlondz

Releia AGENTS/README e a issue atual. Reuse o executor e as provas válidas.
Mapeie scripts de diagnóstico, testes focados, gates finais e smoke que já existem.
Só implemente os comandos que realmente faltarem. Preserve revisão independente,
autorizações de produção e cleanup pós-merge já concedido. Registre no sistema de
medição do Gabriel OS, sem criar outro monitor. Não há implantação automática por
instalar estas skills pessoais.

## Ferramentas complementares

| Item | Situação observada na pesquisa | Próxima decisão |
|---|---|---|
| AI-Memory | Binário local 2.0.0; servidor atual não verificado | Avaliar continuidade e recuperação antes de atualizar |
| ghpending | Não encontrado no PATH consultado | Escolher repos e integração de visualização antes da instalação |
| ai-usagebar | Não encontrado no PATH consultado | Definir provedores e superfície real do desktop |
| ai-jail | Não encontrado no PATH consultado | Piloto isolado que prove o alcance sobre subprocessos e ferramentas |
| tclock | Não encontrado no PATH consultado | Opcional, após haver utilidade para um painel |

Não confundir ausência no PATH com ausência em todo o disco. Nenhum desses programas
foi instalado por este bootstrap. A configuração visual deve usar as instruções de
Omarchy. Não trocar shell, modelo, assinatura, proxy ou política de permissões como
efeito colateral. A disponibilidade nativa de cotas no Codex pode dispensar um widget
se o único interesse for esse provedor.

AI-Memory atual documenta autowire no launcher e autoaprovação de melhorias de memória.
Uma atualização precisa respeitar autorização explícita, escopo registrado e allowlist
do Gabriel OS; este pacote não altera esses componentes. AI-Jail protege o processo
lançado nele, não automaticamente cada conector externo do desktop.

## Critérios para considerar a base operacional

1. Validação e testes do instalador passam.
2. Links apontam para uma única fonte e conflitos preservam dados anteriores.
3. Cada aplicativo descobre as skills em uma nova sessão.
4. Uma tarefa piloto demonstra cumprimento dos gates e entrega evidência útil.
5. Tarefas comparáveis permitem medir melhoria; setup não é benchmark de produtividade.

Os itens 3 a 5 precisam de evidência própria; não são satisfeitos apenas por arquivos
válidos e links corretos.
