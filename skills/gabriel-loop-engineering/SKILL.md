---
name: gabriel-loop-engineering
description: "Definir e executar um ciclo limitado de tentativa, verificação e ajuste com condição observável de sucesso e parada."
---

# Ciclo de execução e verificação

1. Extraia do pedido objetivo, critério observável, executor e verificador. Pergunte apenas pelo que realmente falta; não reinicie uma entrevista se as respostas estão no contexto.
2. Defina sucesso por teste, build, comando, arquivo/artefato, observação ou revisão humana. Existência de arquivo só basta quando é o critério real; arquivo vazio não comprova comportamento. Registre comando/fonte e interpretação.
3. Fixe tentativas, prazo e orçamento. Para iteração local reversível, três tentativas é um limite inicial útil; autorização mais estreita prevalece. Operação real exige limites de recursos, custo, reconciliação e cleanup já acordados. Não reinicie a contagem entre fases.
4. Execute uma tentativa, guarde o primeiro erro sanitizado e classifique a falha. Ajuste só a hipótese sustentada pelos dados. Reutilize recursos compatíveis dentro da sessão autorizada; não destrua fixtures automaticamente após falha recuperável.
5. Pare em sucesso comprovado, cancelamento, limite, perda de ownership/contabilidade, falha crítica ou decisão humana necessária. Resultado desconhecido de mutação precisa ser reconciliado antes de repetir.
6. Use callbacks somente se o runtime os oferece. Caso contrário, acompanhe os processos/ferramentas reais com esperas limitadas e checkpoint. Não invoque APIs fictícias `onLoopComplete` ou `resolveManualReview`. Verificação humana permanece pendente até resposta; tempo decorrido não é aprovação.

## Entrega
Tentativas e evidências, hipótese atual, resultado, recursos retidos/limpos e próxima ação. Não converta “continuar tentando” em gasto ilimitado, retry automático ou nova autorização.

## Saídas extensas com Jev Pruner
Para builds, testes ou instalações não interativas que possam gerar logs extensos, consulte a skill do plugin `jev-pruner` antes de executar. Use seu wrapper original quando o plugin estiver disponível e histórico/saída estiverem autorizados para processamento externo. O My Tools configura OpenRouter com a mesma credencial do Siftr. Não exponha a chave nem a inclua no comando.

Apenas stdout acima de 10 mil tokens estimados pode ser podado. Preserve workdir, argumentos, permissões, checks obrigatórios e critérios de aprovação. Não use para servidores/TTY, leitura de arquivos completos, diffs, dados estruturados ou conteúdo sensível; não aplique também `filter_output` do Siftr ao mesmo resultado. Se faltar runtime, histórico, chave ou rede, execute normalmente e registre a limitação.

O wrapper mantém stderr/exit code e guarda o original no arquivo indicado pelo rodapé. Recupere-o quando faltar contexto. Só registre poda com marcador de omissão; menos texto não prova economia total nem um teste aprovado. Em Cloud, repositórios presentes não substituem instalação, credencial, rede e hook/histórico da sessão.
