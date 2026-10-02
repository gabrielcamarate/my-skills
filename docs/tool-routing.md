# Escolha das ferramentas instaladas

Antes da primeira operação elegível, escolha pela necessidade e capacidades desta sessão.
Não repita discovery a cada comando nem carregue todo o catálogo. Use o registro existente
para anotar ferramenta/interface e resultado; em fallback elegível, anote um motivo concreto.
Instalação, disponibilidade, chamada executada e benefício medido são estados distintos.

| Necessidade | Rota |
|---|---|
| Arquivo já confirmado / identificador exato | Leitura direta / `rg`, sem inferência |
| Comportamento sem localização confirmada | Siftr `semantic_search`, se conectado e envio autorizado |
| Feedback de uma suíte lenta durante iteração | Skill upstream `jev-test-filter` e CLI; gates finais continuam completos |
| stdout potencialmente extenso, não interativo | Skill `jev-pruner` e wrapper, se histórico inteiro e saída autorizados; exigir marcador antes de alegar poda |
| Fluxo funcional em navegador isolado | Preferir `jev-playwright` ou CLI `jev-browser`; comandos nativos para alvos conhecidos, `browser_run` para metas adequadas |
| Aba/perfil pessoal indicado pelo usuário | Preservar a conexão e conta existentes; não migrar cookies para navegador isolado |
| QA visual | Usar superfície que exponha pixels e viewport necessária; Jev screen quando disponível, ou CUA/capacidade visual adequada |

Fallback: capacidade ausente/falhou, cenário incompatível, dados não autorizados ou rota
nativa mais adequada ao critério. Não trocar silenciosamente uma rota elegível por hábito,
nem chamar o modelo apenas para demonstrar uso. Reconcilie mutação incerta antes de trocar
ferramenta; preserve gates, ownership e cleanup. Não instale/configure clientes por efeito
colateral. Sessões antigas podem manter um catálogo anterior: verificar disponibilidade
real uma vez. Links locais não configuram automaticamente MCPs, plugins ou Cloud.
