#!/usr/bin/env bash
# The fast core an agent must pass before opening a PR (#327): lint, typecheck,
# unit tests and build, without credentials or local services. Run before every push.
# Heavy gates run after merge on staging and before promotion to main.
set -Eeuo pipefail

ROOT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT_DIR"
"$ROOT_DIR/scripts/ensure-node.sh" --check

# Same public dummies as the PR workflow, forced so real credentials in the shell
# or in .env.local are never used.
# __DUMMY_ENV__: variáveis falsas e públicas que o build/testes exigem (nunca segredos reais)
export NODE_OPTIONS=--max-old-space-size=4096

step() { printf '\n==> %s\n' "$1"; }
step 'workflow helper'; python3 scripts/__PROJECT__-workflow.py doctor >/dev/null
step 'workflow contracts'; python3 -m unittest discover -s scripts/tests -p 'test_*.py'
step lint; pnpm lint
step typecheck; pnpm typecheck
step 'unit tests'; pnpm test
step build; pnpm build
printf '\nPASS  fast core\n'
