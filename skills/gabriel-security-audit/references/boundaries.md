# Fronteiras e validação adversarial

## Inventário proporcional

Selecione fronteiras presentes no escopo. Não invente superfícies para preencher
um relatório nem transforme toda mudança pequena em auditoria de sistema inteiro.

- Identidade/sessão: criação, validação, expiração, revogação e troca de privilégio.
- Autorização: ação, objeto, papel, tenant e default diante de identidade ausente.
- Isolamento: identidade completa em storage, índices, cache, busca e arquivos.
- Injeção: shell/argv, SQL, templates, paths/symlinks, parsing e normalização.
- Privacidade: coleta, retenção, logs, erros e sanitização na fronteira responsável.
- Execução: subprocessos, plugins/hooks, configuração capaz de alterar capabilities.
- Integridade: transações, escrita atômica, ownership, retries e concorrência.
- Rede: bind, TLS, redirects, resolução de endereços, SSRF e limites de recursos.
- Criptografia: primitivas estabelecidas, aleatoriedade, chaves/nonces e lifecycle.

## Evidência automatizada

Use scanners, alertas de dependência, análise estática, secret scanning e testes
existentes como pistas. Associe-os ao candidato e à configuração. Alerta sem
caminho real fica como hipótese; ausência de alerta não comprova ausência de bug.
Consulta de alertas não autoriza dismiss, rotação, alteração de política ou
divulgação pública. Material sensível deve ser descrito de forma sanitizada.

## Prova

Para um caso confirmado, documente capacidade inicial do atacante, entrada,
fronteira que deveria bloquear, caminho até operação sensível e efeito observável.
Tente refutar antes de concluir: controle anterior, validação, inacessibilidade,
normalização, contexto de confiança ou ausência do privilégio pressuposto.

Quando permitido, use fixtures sintéticas e canários inertes. Compare caso legítimo
e caso adversarial. Teste errado-tenant/papel, identidade ausente ou parcial,
expiração/revogação, caminhos alternativos, normalização, tamanho/tempo, retry,
cancelamento e concorrência somente quando ligados ao achado. SSRF não autoriza
consultar metadata real; use destino sintético isolado.

Uma regressão deve detectar o controle ausente ou quebrado quando possível. Não
remova um controle de produção para demonstrá-lo. Se a prova depende de ambiente
indisponível, descreva exatamente o que falta e mantenha a classificação provisória.

## Resultado

Severidade expressa impacto e pré-requisitos; confiança expressa força da prova.
Mantenha esses eixos separados. Liste candidatos refutados com causa, fronteiras
revisadas com evidência e lacunas. Correção e verificação precisam preservar o
caminho legítimo, não apenas bloquear qualquer entrada e fazer o ataque falhar.
