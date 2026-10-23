#!/usr/bin/env bash
# Make the project's exact pnpm (packageManager pin) available under
# $NODE_PREFIX/lib/pinned-pnpm/<version>/bin. Installs it with the npm of the
# Node already first on PATH (the pinned one, see cloud-setup.sh), only when
# neither PATH nor that directory has it. Never writes the shared
# $NODE_PREFIX/bin: it may hold another project's node, which would then shadow
# the pinned one. Callers put --bin first on their own PATH (see fast-check.sh).
#   ./scripts/ensure-pnpm.sh          install if `pnpm` on PATH is another version
#   ./scripts/ensure-pnpm.sh --bin    print the pinned bin dir (installs nothing)
#   ./scripts/ensure-pnpm.sh --check  only verify the version on PATH
set -Eeuo pipefail

PNPM_VERSION=10.18.1
NODE_PREFIX=${NODE_PREFIX:-$HOME/.local}
INSTALL_ROOT="$NODE_PREFIX/lib/pinned-pnpm"
INSTALL_DIR="$INSTALL_ROOT/$PNPM_VERSION"
fail() { printf 'FAIL  %s\n' "$1" >&2; exit 1; }

case "${1:-}" in
  '') ;;
  --bin) printf '%s\n' "$INSTALL_DIR/bin"; exit 0 ;;
  --check)
    found=$(pnpm --version 2>/dev/null || true)
    [[ "$found" == "$PNPM_VERSION" ]] \
      || fail "pnpm $PNPM_VERSION is required, found ${found:-none}; run ./scripts/cloud-setup.sh and prepend $INSTALL_DIR/bin to PATH (./scripts/ensure-pnpm.sh --bin)"
    exit 0 ;;
  *) printf 'usage: %s [--bin|--check]\n' "$0" >&2; exit 2 ;;
esac

installed() { [[ "$("$1/bin/pnpm" --version 2>/dev/null || true)" == "$PNPM_VERSION" ]]; }
[[ "$(pnpm --version 2>/dev/null || true)" == "$PNPM_VERSION" ]] && exit 0
installed "$INSTALL_DIR" && exit 0

mkdir -p -- "$INSTALL_ROOT"
# Sessions installing the same version take turns. Without flock (macOS) the
# install still fails closed.
if command -v flock >/dev/null 2>&1; then
  exec {install_lock}>>"$INSTALL_ROOT/.install.lock"
  flock -w 600 "$install_lock" || fail "another session is still installing pnpm $PNPM_VERSION"
fi

if ! installed "$INSTALL_DIR"; then
  TMP=$(mktemp -d "$INSTALL_ROOT/.install.XXXXXX")
  trap 'rm -rf -- "$TMP"' EXIT
  # pnpm has no install scripts; refusing them keeps the install to unpacking.
  npm install --global --ignore-scripts --no-update-notifier --no-fund --no-audit \
    --prefix "$TMP" "pnpm@$PNPM_VERSION" >/dev/null || fail "unable to install pnpm $PNPM_VERSION"
  installed "$TMP" || fail "npm did not install pnpm $PNPM_VERSION"
  # Another session may finish the same install first; keep whichever landed.
  installed "$INSTALL_DIR" || { rm -rf -- "$INSTALL_DIR"; mv -- "$TMP" "$INSTALL_DIR" 2>/dev/null || true; }
  installed "$INSTALL_DIR" || fail "unable to install $INSTALL_DIR"
fi

printf 'PASS  pnpm %s at %s\n' "$PNPM_VERSION" "$INSTALL_DIR/bin/pnpm"
