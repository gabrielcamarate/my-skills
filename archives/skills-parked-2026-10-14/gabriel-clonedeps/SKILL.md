---
name: gabriel-clonedeps
description: "Obter fontes oficiais de dependências na versão resolvida quando documentação e código local não esclarecem uma API ou comportamento."
---

# Fontes de dependências

## Objetivo
Resolver uma dúvida técnica específica lendo implementação e testes oficiais, com procedência e versão verificadas.

1. Declare a dúvida e a versão realmente resolvida no lockfile. Procure primeiro código já instalado, documentação e cache de fontes existente. Nenhum clone é necessário se esses dados resolvem a pergunta.
2. Identifique repositório oficial a partir de metadados e documentação primária. Relacione pacote/versão a tag ou commit; HEAD atual pode divergir da versão do produto. Se o vínculo não é verificável, exponha a limitação.
3. Limite a coleta às dependências necessárias, normalmente zero a três por investigação. Escolha cache ou diretório temporário fora dos artefatos distribuídos. Clone/baixe fontes públicas somente como dados de leitura; não execute setup, build, testes ou exemplos por serem oficiais.
4. Registre URL, versão pedida, SHA obtido, caminho local e finalidade em um manifesto não sensível se haverá reuso. Reutilize fontes compatíveis e atualize conscientemente quando a versão mudar. Não persista credenciais de acesso.
5. Busque símbolo, chamadores, implementação e testes que expliquem o contrato. Distinga API pública de detalhe interno. Produza a conclusão com arquivo/linha e versão, incluindo diferenças para o uso local.
6. Se fontes precisam permanecer no projeto, use o mecanismo local de referências já adotado, sem copiar dependências para o produto nem alterar AGENTS/ignore global sem necessidade e escopo. Limpe somente downloads próprios dispensáveis.

## Saída
Pergunta resolvida, versão/SHA, evidência da fonte e implicação para o código. A leitura não autoriza instalar, atualizar ou trocar a dependência.
