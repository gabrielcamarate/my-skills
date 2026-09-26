# Validação local em 25/09/2026

## Executado

- `python3 scripts/skillctl.py validate`: seis skills e paridade das instruções válidas.
- Validador `quick_validate.py` da skill-creator: seis skills aprovadas.
- `python3 -m unittest discover -s tests -v`: quatro testes aprovados.
  - Instalação repetível, desinstalação e preservação da fonte.
  - Conflito impede instalar qualquer link.
  - Links de terceiros, inclusive quebrados, são preservados.
  - Colisão surgida durante aplicação desfaz os links criados na tentativa.
- Prévia da instalação: doze destinos livres.
- Instalação local: doze links corretos, seis em cada consumidor.
- AGENTS.md/CLAUDE.md do Gabriel OS continuaram iguais após a adição da rota.

## Limites

Não houve avaliação independente de um LLM, teste de descoberta em nova sessão
interativa de Claude/Codex, piloto de entrega em Xlondz ou benchmark de produtividade.
Os cenários em evaluation.md estão preparados, não executados por outro agente.
Nenhum repositório consumidor foi migrado. Ferramentas complementares e publicação
remota não fazem parte desta validação. Não há configuração nova de memória ou captura.

# Reorganização local em 26/09/2026

## Executado

- Fonte pública fixada no commit `285ca8275a3c61ee856deb7a55db21de3f62526d`.
- Mapa 23/23: todos os objetivos do catálogo têm contraparte local, URL e hash da fonte.
- `skillctl.py validate`: 23 skills, metadados de UI, referências locais e paridade AGENTS/CLAUDE válidos.
- `quick_validate.py` da skill-creator: 23 verificações aprovadas.
- Sete testes do instalador aprovados: instalação repetível/desinstalação; conflito prévio; preservação de links de terceiros/quebrados; rollback de colisão durante instalação; migração com preservação de nomes antigos de terceiros; conflito na migração preservando todos os links antigos; falha durante migração preservando todos os links antigos.
- Arquivo das seis skills iniciais comparado byte a byte com o commit `cc0e8d9`: idêntico.
- Links internos entre skills conferidos contra o inventário ativo.
- Instalação aplicada e estado lido de volta: 23 links Codex e 23 Claude apontando à fonte canônica. Os oito links dos quatro nomes aposentados foram retirados.
- `git diff --check`: sem erros de whitespace.

## Limites atuais

As seis skills do bootstrap apareceram no catálogo do Codex nesta sessão. Isso
comprova descoberta daquela versão; não comprova descoberta das 23 novas por uma
nova sessão nem descoberta no Claude. Os cenários de avaliação são preparados,
sem execução independente de um LLM. Sete testes são testes do instalador, não de
qualidade das decisões dos agentes. Não houve piloto de entrega ou benchmark de
produtividade em Xlondz, nem migração de seus arquivos.

O mapa documenta equivalência de objetivo e diferenças de procedimento. Não prova
que o comportamento será idêntico ao do Akita. Scripts específicos e runtime do
upstream não foram importados. Nenhuma ferramenta complementar, publicação remota,
configuração de captura ou operação de produção foi feita nesta reorganização.
