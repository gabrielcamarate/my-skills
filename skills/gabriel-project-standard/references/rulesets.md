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

## Promoção: main só merge commit (projetos com staging)

O "Padrão: main" do enterprise aceita squash e merge commit, porque os projetos sem staging entregam na `main` por squash. Num projeto com staging, a `main` só recebe a promoção, e um ruleset de repo restringe o método a merge commit (decisão de 22/10/2026). Motivo: o squash para a `main` escapava do ask do `settings.json` (só `--merge` pergunta), e um squash seguido de merge commit podia levar à `main` conteúdo não testado, com árvore diferente da ponta da `staging` cuja pesada ficou verde. Com merge commit, o 2º pai é a ponta promovida e o `main-ready --sha` do deploy confere a árvore.

```bash
R=__OWNER__/__REPO__
gh api -X POST repos/$R/rulesets --input - <<J
{"name":"Promoção: main só merge commit","target":"branch","enforcement":"active",
 "conditions":{"ref_name":{"include":["refs/heads/main"],"exclude":[]}},
 "rules":[{"type":"pull_request","parameters":{"required_approving_review_count":0,"dismiss_stale_reviews_on_push":false,"require_code_owner_review":false,"require_last_push_approval":false,"required_review_thread_resolution":true,"allowed_merge_methods":["merge"]}}]}
J
```

Quando vários rulesets valem na mesma branch, o GitHub aplica a interseção dos métodos de merge: enterprise (squash e merge) com este (merge) deixa só merge commit. Não ligue `allow_merge_commit=false` no repo: a promoção precisa dele. Confira com `gh api repos/$R/rules/branches/main`: dois `pull_request`, um `Enterprise` e um `Repository` com `allowed_merge_methods: ["merge"]`. Projeto sem staging não cria este ruleset.
