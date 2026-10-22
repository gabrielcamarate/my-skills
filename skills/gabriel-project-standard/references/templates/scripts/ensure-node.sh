#!/usr/bin/env bash
# Make the project's exact Node.js (.nvmrc and CI pin) available under
# $NODE_PREFIX/lib/pinned-node/<build>/bin. Downloads the official build from
# nodejs.org only when needed, verifies it against the published SHASUMS256.txt
# and installs it idempotently. Never touches the shared $NODE_PREFIX/bin:
# projects with different pins share the machine, so each process puts its own
# pinned bin dir first on PATH (see fast-check.sh).
#   ./scripts/ensure-node.sh          install if `node` on PATH is another version
#   ./scripts/ensure-node.sh --bin    print the pinned bin dir (installs nothing)
#   ./scripts/ensure-node.sh --check  only verify the version on PATH
set -Eeuo pipefail

NODE_VERSION=22.20.0
NODE_PREFIX=${NODE_PREFIX:-$HOME/.local}
NODE_DIST_URL=${NODE_DIST_URL:-https://nodejs.org/dist}
case "$NODE_DIST_URL" in https://*|file://*) ;; *) printf 'FAIL  NODE_DIST_URL must be https:// or file://\n' >&2; exit 1 ;; esac
fail() { printf 'FAIL  %s\n' "$1" >&2; exit 1; }

path_version() { node --version 2>/dev/null || true; }
platform() {
  local os arch
  case "$(uname -s)" in Linux) os=linux ;; Darwin) os=darwin ;; *) fail "unsupported OS $(uname -s)" ;; esac
  case "$(uname -m)" in x86_64|amd64) arch=x64 ;; aarch64|arm64) arch=arm64 ;; *) fail "unsupported CPU $(uname -m)" ;; esac
  printf '%s-%s\n' "$os" "$arch"
}
sha256() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1
  else shasum -a 256 "$1" | cut -d' ' -f1; fi
}

NAME="node-v$NODE_VERSION-${NODE_DIST_PLATFORM:-$(platform)}"
INSTALL_ROOT="$NODE_PREFIX/lib/pinned-node"
INSTALL_DIR="$INSTALL_ROOT/$NAME"

case "${1:-}" in
  '') ;;
  --bin) printf '%s\n' "$INSTALL_DIR/bin"; exit 0 ;;
  --check)
    found=$(path_version)
    [[ "$found" == "v$NODE_VERSION" ]] \
      || fail "Node $NODE_VERSION is required, found ${found:-none}; run ./scripts/cloud-setup.sh and prepend $INSTALL_DIR/bin to PATH (./scripts/ensure-node.sh --bin)"
    exit 0 ;;
  *) printf 'usage: %s [--bin|--check]\n' "$0" >&2; exit 2 ;;
esac

[[ "$(path_version)" == "v$NODE_VERSION" ]] && exit 0

installed() { [[ -x "$INSTALL_DIR/bin/node" && "$("$INSTALL_DIR/bin/node" --version 2>/dev/null)" == "v$NODE_VERSION" ]]; }

if ! installed; then
  mkdir -p -- "$INSTALL_ROOT"
  TMP=$(mktemp -d "$INSTALL_ROOT/.download.XXXXXX")
  trap 'rm -rf -- "$TMP"' EXIT
  ARCHIVE="$NAME.tar.gz"
  curl -fsSL --proto-redir =https --retry 3 -o "$TMP/SHASUMS256.txt" "$NODE_DIST_URL/v$NODE_VERSION/SHASUMS256.txt" \
    || fail "unable to download SHASUMS256.txt for Node $NODE_VERSION"
  expected=$(awk -v f="$ARCHIVE" '$2 == f { print $1 }' "$TMP/SHASUMS256.txt")
  [[ "$expected" =~ ^[0-9a-f]{64}$ ]] || fail "no SHA256 for $ARCHIVE in SHASUMS256.txt"
  curl -fsSL --proto-redir =https --retry 3 -o "$TMP/$ARCHIVE" "$NODE_DIST_URL/v$NODE_VERSION/$ARCHIVE" \
    || fail "unable to download $ARCHIVE"
  actual=$(sha256 "$TMP/$ARCHIVE")
  [[ "$actual" == "$expected" ]] || fail "SHA256 mismatch for $ARCHIVE (expected $expected, got $actual)"
  tar --no-same-owner -xzf "$TMP/$ARCHIVE" -C "$TMP"
  [[ "$("$TMP/$NAME/bin/node" --version)" == "v$NODE_VERSION" ]] || fail "$ARCHIVE does not contain Node $NODE_VERSION"
  # Another session may finish the same install first; keep whichever landed.
  installed || { rm -rf -- "$INSTALL_DIR"; mv -- "$TMP/$NAME" "$INSTALL_DIR" 2>/dev/null || true; }
  installed || fail "unable to install $INSTALL_DIR"
fi

printf 'PASS  Node %s at %s\n' "$NODE_VERSION" "$INSTALL_DIR/bin/node"
