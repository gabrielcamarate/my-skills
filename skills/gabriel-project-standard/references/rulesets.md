# Rulesets (gh api)

Requer repositório em org da enterprise (repo pessoal privado não aceita). `CHECK` é o nome do job obrigatório do `pr.yml`.

```bash
R=__OWNER__/__REPO__; CHECK=release-quality
gh api -X PATCH repos/$R -F allow_auto_merge=true -F delete_branch_on_merge=true -F allow_merge_commit=true -F allow_squash_merge=true
rule() { # $1 nome, $2 branch, $3 métodos JSON, $4 strict
gh api -X POST repos/$R/rulesets --input - <<J
{"name":"$1","target":"branch","enforcement":"active",
 "conditions":{"ref_name":{"include":["refs/heads/$2"],"exclude":[]}},
 "rules":[{"type":"deletion"},{"type":"non_fast_forward"},
  {"type":"pull_request","parameters":{"required_approving_review_count":0,"dismiss_stale_reviews_on_push":false,"require_code_owner_review":false,"require_last_push_approval":false,"required_review_thread_resolution":false,"allowed_merge_methods":$3}},
  {"type":"required_status_checks","parameters":{"strict_required_status_checks_policy":$4,"required_status_checks":[{"context":"$CHECK"}]}}]}
J
}
rule "Protect staging branch" staging '["squash"]' false
rule "Protect main branch" main '["squash","merge"]' true
```

Confira depois: `gh api repos/$R/rulesets --jq '.[].name'`. Sem regra `merge_queue`.
