---
name: gabriel-security-audit
description: "Auditar segurança de um escopo de código definido, validando caminhos de ataque e controles sem confundir alertas com vulnerabilidades."
---

# Auditoria de segurança

## Objetivo
Produzir achados demonstráveis em um escopo e revisão identificados. Auditoria não concede autorização para exploração externa, alteração de produção, rotação de chaves ou fechamento de alertas.

1. Defina ativos, atores, entradas, fronteiras de confiança, privilégios, ambientes permitidos e exclusões. Separe código próprio, dependência e material não confiável. Não execute payload suspeito no host.
2. Inventarie superfícies e controles. Leia [fronteiras e validação](references/boundaries.md) para a revisão. Use o plugin de segurança instalado quando seu procedimento corresponde à tarefa: `codex-security:security-scan` para auditoria normal, `deep-security-scan` somente para escopo profundo solicitado. Leia a skill disponível antes de usá-la; sem plugin, siga este procedimento diretamente.
3. Reúna scanners e alertas já existentes, associados ao candidato correto. Não confunda severidade do scanner com explorabilidade. Nunca imprima segredo para provar vazamento; registre localização e classe com redação segura.
4. Para cada candidato, trace entrada controlável → transformações → controle esperado → operação sensível → impacto. Tente refutar: permissões anteriores, validação, normalização, isolamento, limites e inviabilidade operacional.
5. Quando autorizado e necessário, crie prova sintética isolada com controle positivo legítimo e caso adversarial. Verifique que o teste distingue ausência do controle de comportamento permitido; não explore sistemas reais fora do escopo. Declare limites de reprodução.
6. Use revisão independente quando o projeto exigir e houver executor autorizado. Se feita pelo próprio agente, identifique como autorrevisão. Classifique confirmado, refutado ou precisa de validação, com severidade e confiança separadas.
7. Proponha correção na fronteira responsável e regressão que prova a restauração do controle. Implementação só dentro da autorização existente. Verificação de correção não substitui revisão do efeito colateral.

## Entrega
Achados ordenados com arquivo/linha, pré-requisitos do atacante, caminho, impacto, prova, correção e limitações. Liste fronteiras examinadas sem achado, hipóteses rejeitadas e escopo não testado. Zero achados não significa certificado de segurança.
