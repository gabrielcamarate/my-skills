#!/usr/bin/env bash
# Prepare a fresh agent environment (Codex/Claude cloud or a clean machine) for
# ./scripts/fast-check.sh. Idempotent; needs network, never needs credentials.
set -Eeuo pipefail

ROOT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
PNPM_VERSION=10.18.1
NODE_PREFIX=${NODE_PREFIX:-$HOME/.local}
fail() { printf 'FAIL  %s\n' "$1" >&2; exit 1; }

# Exact Node from .nvmrc; installs the verified official build only when needed.
# Only this process gets it first on PATH; fast-check.sh does the same.
"$ROOT_DIR/scripts/ensure-node.sh"
PATH="$("$ROOT_DIR/scripts/ensure-node.sh" --bin):$PATH"
export PATH

if [[ "$(pnpm --version 2>/dev/null || true)" != "$PNPM_VERSION" ]]; then
  PNPM_PREFIX=${PNPM_PREFIX:-$NODE_PREFIX}
  npm install --global --prefix "$PNPM_PREFIX" "pnpm@$PNPM_VERSION" >/dev/null
  export PATH="$PNPM_PREFIX/bin:$PATH"
  [[ "$(pnpm --version)" == "$PNPM_VERSION" ]] || fail "pnpm $PNPM_VERSION not on PATH; add $PNPM_PREFIX/bin"
fi

# Cloud sessions commit as the repository owner, like local work.
if [[ "${CLAUDE_CODE_REMOTE:-}" == true ]]; then
  [[ '__GIT_NAME__' != __* ]] || { echo 'cloud-setup: preencha a identidade git noreply' >&2; exit 1; }
  git config --global user.name '__GIT_NAME__'
  git config --global user.email '__GIT_NOREPLY_EMAIL__'
fi

(cd "$ROOT_DIR" && pnpm install --frozen-lockfile)
"$ROOT_DIR/scripts/ensure-node.sh" --check
printf 'PASS  environment ready; next: ./scripts/fast-check.sh\n'
