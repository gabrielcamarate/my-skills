# Rulesets (gh api)

Requer repositório numa org da enterprise `camaratetech` (rakmma, xlondz, maison-eclat); repo pessoal privado não aceita. A proteção se divide em duas camadas (aplicada em 16/10/2026):

- **Enterprise** (já vale para todo repo de toda org): rulesets "Padrão: staging" e "Padrão: main" com `deletion`, `non_fast_forward` e `pull_request` (0 aprovações, conversas resolvidas; `staging` só squash; `main` squash e merge commit). Dependabot alerts, security updates e dependency graph vêm da configuração de segurança "Padrão Camarate Tech", padrão para todo repo novo (sem Advanced Security).
- **Repo** (este script): só um ruleset por branch com `required_status_checks`, porque o check muda por projeto, e os botões de merge.

`CHECK` é o nome do job obrigatório do `pr.yml`.

```bash
R=__OWNER__/__REPO__; CHECK=release-quality
gh api -X PATCH repos/$R -F allow_squash_merge=true -F allow_merge_commit=true -F allow_rebase_merge=false -F allow_auto_merge=true -F delete_branch_on_merge=true -F allow_update_branch=true
rule() { # $1 nome, $2 branch
gh api -X POST repos/$R/rulesets --input - <<J
{"name":"$1","target":"branch","enforcement":"active",
 "conditions":{"ref_name":{"include":["refs/heads/$2"],"exclude":[]}},
 "rules":[{"type":"required_status_checks","parameters":{"strict_required_status_checks_policy":false,"required_status_checks":[{"context":"$CHECK","integration_id":15368}]}}]}
J
}
rule "Protect staging branch" staging
rule "Protect main branch" main
```

Não repita no repo as regras do enterprise. Sem `strict`: a promoção por merge commit deixa a `staging` sempre atrás da `main`, e `strict` travaria a segunda promoção; o gate de promoção garante o SHA exato. `integration_id` 15368 = GitHub Actions (status manual não satisfaz). O POST não é idempotente: confira antes se o ruleset já existe.

Confira depois: `gh api repos/$R/rules/branches/main` (e `staging`) lista `deletion`, `non_fast_forward` e `pull_request` com `ruleset_source_type: Enterprise` e `required_status_checks` com `Repository`. Sem regra `merge_queue`.
