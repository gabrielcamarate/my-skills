#!/usr/bin/env bash
# Make the project's exact pnpm (packageManager pin) available under
# $NODE_PREFIX/lib/pinned-pnpm/<version>/bin. Installs it with the npm of the
# pinned Node (ensure-node.sh), only when neither PATH nor that directory has
# it. Never writes the shared $NODE_PREFIX/bin: it may hold another project's
# node, which would then shadow the pinned one. Callers put --bin first on their
# own PATH (see fast-check.sh).
#   ./scripts/ensure-pnpm.sh          install if `pnpm` on PATH is another version
#   ./scripts/ensure-pnpm.sh --bin    print the pinned bin dir (installs nothing)
#   ./scripts/ensure-pnpm.sh --check  only verify the version on PATH
set -Eeuo pipefail

PNPM_VERSION=10.18.1
NODE_PREFIX=${NODE_PREFIX:-$HOME/.local}
INSTALL_ROOT="$NODE_PREFIX/lib/pinned-pnpm"
INSTALL_DIR="$INSTALL_ROOT/$PNPM_VERSION"
fail() { printf 'FAIL  %s\n' "$1" >&2; exit 1; }
# pnpm 10 delegates to the packageManager pin and answers its version, then
# downloads it on first use (and hangs with an empty HOME). Ask for the real one.
pnpm_version() { npm_config_manage_package_manager_versions=false "$1" --version 2>/dev/null || true; }

case "${1:-}" in
  '') ;;
  --bin) printf '%s\n' "$INSTALL_DIR/bin"; exit 0 ;;
  --check)
    found=$(pnpm_version pnpm)
    [[ "$found" == "$PNPM_VERSION" ]] \
      || fail "pnpm $PNPM_VERSION is required, found ${found:-none}; run ./scripts/cloud-setup.sh and prepend $INSTALL_DIR/bin to PATH (./scripts/ensure-pnpm.sh --bin)"
    exit 0 ;;
  *) printf 'usage: %s [--bin|--check]\n' "$0" >&2; exit 2 ;;
esac

# The pinned Node and its npm do the install, even when this runs on its own
# with another project's node first on PATH.
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PATH="$("$SCRIPT_DIR/ensure-node.sh" --bin):$PATH"
"$SCRIPT_DIR/ensure-node.sh" --check

installed() { [[ "$(pnpm_version "$1/bin/pnpm")" == "$PNPM_VERSION" ]]; }
[[ "$(pnpm_version pnpm)" == "$PNPM_VERSION" ]] && exit 0
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
