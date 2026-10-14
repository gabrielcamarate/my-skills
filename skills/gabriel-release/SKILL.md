---
name: gabriel-release
description: "Conferir ou preparar uma release: versão ligada ao SHA exato, publicação pelo mecanismo do projeto e smoke do artefato entregue."
---

# Release

Versão, tag e entrega ligadas ao mesmo SHA. O mecanismo vem do `AGENTS.md` e dos docs do projeto. Exemplo vivo: Xlondz.

1. Descubra como o projeto publica. No Xlondz, a versão já vem no PR (`release cut`) e a publicação é automática depois do merge com o CI da main verde: a skill **verifica**, não publica à mão. Projeto sem automação: a versão sai da classificação do CHANGELOG e o resto segue o doc dele.
2. Confirme que a tag e a release apontam para o SHA do squash e que o CI da main passou **nesse SHA**. Tag anotada, nunca movida nem reescrita. Em timeout, reconcilie o estado antes de repetir.
3. Smoke do **artefato entregue**, não do checkout (Xlondz: `scripts/artifact_smoke.py` e os smokes do deploy).
4. Separe "publicado" de "em produção": confira o deploy do mesmo artefato e a versão ativa. Deploy que ficou para trás (`NO_RUNTIME_CHANGE` não é deploy de código) entra no relatório. Source: xlondz#520.
5. Release só quando pedida ou quando o fluxo do projeto a dispara. Nunca corte release que ninguém pediu.
