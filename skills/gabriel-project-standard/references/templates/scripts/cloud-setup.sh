#!/usr/bin/env bash
# Prepare a fresh agent environment (Codex/Claude cloud or a clean machine) for
# ./scripts/fast-check.sh. Idempotent; needs network, never needs credentials.
set -Eeuo pipefail

ROOT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)

# Exact Node from .nvmrc; installs the verified official build only when needed.
# Only this process gets it first on PATH; fast-check.sh does the same.
"$ROOT_DIR/scripts/ensure-node.sh"
PATH="$("$ROOT_DIR/scripts/ensure-node.sh" --bin):$PATH"
export PATH

# Exact pnpm in its own per-version directory, also first only on this PATH.
# Never the shared ~/.local/bin, whose node would shadow the pinned one (#12).
"$ROOT_DIR/scripts/ensure-pnpm.sh"
PATH="$("$ROOT_DIR/scripts/ensure-pnpm.sh" --bin):$PATH"
export PATH
"$ROOT_DIR/scripts/ensure-pnpm.sh" --check

# Cloud sessions commit as the repository owner, like local work.
if [[ "${CLAUDE_CODE_REMOTE:-}" == true ]]; then
  [[ '__GIT_NAME__' != __* ]] || { echo 'cloud-setup: preencha a identidade git noreply' >&2; exit 1; }
  git config --global user.name '__GIT_NAME__'
  git config --global user.email '__GIT_NOREPLY_EMAIL__'
fi

(cd "$ROOT_DIR" && pnpm install --frozen-lockfile)
"$ROOT_DIR/scripts/ensure-node.sh" --check
printf 'PASS  environment ready; next: ./scripts/fast-check.sh\n'
