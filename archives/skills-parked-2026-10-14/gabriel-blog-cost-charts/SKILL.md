---
name: gabriel-blog-cost-charts
description: "Criar gráficos de qualidade, custo e tempo para resultados comparáveis de benchmarks, com fontes e limites explícitos."
---

# Gráficos de custo e resultado

## Objetivo
Tornar comparáveis resultados de benchmark sem fabricar economia. Use para gráficos solicitados ou análise visual de medições reais, não para justificar um modelo favorito.

1. Identifique dataset autorizado e unidade de comparação. Em Gabriel OS, use registros existentes de benchmarks quando esse for o escopo. Não abra projetos ou memórias adicionais por recência.
2. Separe tarefas, versões, modelos/esforço, qualidade/aceite, tempo decorrido, tempo ativo e custos. Não some intervalos sobrepostos nem chame duração de turno de tempo de raciocínio. Retrospectivas ficam identificadas.
3. Distinga custo API medido, estimativa documentada, assinatura e valor desconhecido. Não atribua zero a dado ausente. Compare populações e critérios equivalentes; exponha tamanho de amostra, exclusões e falta de comparabilidade.
4. Escolha scatter custo×qualidade, com tamanho indicando tempo, quando as três grandezas são válidas. Escala log exige custo positivo. Um ranking qualidade/(custo×tempo) é apenas um índice escolhido, sensível a unidades e zeros; publique fórmula e limites, nunca o trate como produtividade universal.
5. Gere artefato local com a ferramenta de gráficos disponível e adequada. Use idioma, tema e formatos pedidos; pt-BR é o padrão. Não exija Hugo, S3 ou versão inglesa sem necessidade.
6. Inspecione cada imagem: rótulos sobrepostos, eixos cortados, legenda, unidades, contraste e notas. Confira manualmente pontos e índices. Dados indisponíveis devem permanecer visíveis como exclusão explicada, não desaparecer silenciosamente.
7. Entregue gráfico e dados/metodologia suficientes para reproduzir. Upload e publicação são etapas separadas com destino e autorização próprios. Não leia arquivos de segredos para reproduzir o comando S3 do original.

## Saída
Artefatos, fonte/datagem, critérios de inclusão, fórmula e limites. Não alegue ganho de velocidade ou custo entre tarefas incomparáveis.
