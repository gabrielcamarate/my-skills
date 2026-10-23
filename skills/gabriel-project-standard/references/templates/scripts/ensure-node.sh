#!/usr/bin/env bash
# Make the project's exact Node.js (.nvmrc and CI pin) available under
# $NODE_PREFIX/lib/pinned-node/<build>/bin. Downloads the official build from
# nodejs.org only when needed, verifies it against the published SHASUMS256.txt
# and installs it idempotently (temp dir, atomic rename, flock between sessions).
# Never touches the shared $NODE_PREFIX/bin: projects with different pins share
# the machine, so each process puts its own pinned bin dir first on PATH (see
# fast-check.sh).
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

installed() { [[ -x "$1/bin/node" && "$("$1/bin/node" --version 2>/dev/null)" == "v$NODE_VERSION" ]]; }
if ! installed "$INSTALL_DIR"; then
  mkdir -p -- "$INSTALL_ROOT"
  # Sessions installing the same build take turns. Without flock (macOS) the
  # rename below never replaces a working install; sessions racing over a broken
  # leftover may still fail closed or lose the install, and a rerun installs it.
  if command -v flock >/dev/null 2>&1; then
    exec {install_lock}>>"$INSTALL_ROOT/.$NAME.lock"
    flock -w 600 "$install_lock" || fail "another session is still installing Node $NODE_VERSION"
  fi
fi

# Checked again under the lock: the session before us may have installed it.
if ! installed "$INSTALL_DIR"; then
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
  installed "$TMP/$NAME" || fail "$ARCHIVE does not contain Node $NODE_VERSION"
  # A rename never replaces an existing install (GNU mv -T fails on a non-empty
  # dir), so the first build to land wins and is never removed under a running
  # session. BSD mv would nest into a dir that appeared meanwhile; that copy goes.
  # A broken leftover is renamed into $TMP (removed on exit), never deleted in place.
  land() {
    if mv --version >/dev/null 2>&1; then mv -T -- "$TMP/$NAME" "$INSTALL_DIR" 2>/dev/null
    else
      [[ ! -e "$INSTALL_DIR" ]] && mv -- "$TMP/$NAME" "$INSTALL_DIR" 2>/dev/null || return 1
      [[ ! -e "$INSTALL_DIR/$NAME" ]] || { rm -rf -- "$INSTALL_DIR/$NAME"; return 1; }
    fi
  }
  land || installed "$INSTALL_DIR" || { mv -- "$INSTALL_DIR" "$TMP/broken" 2>/dev/null || true; land || true; }
  installed "$INSTALL_DIR" || fail "unable to install $INSTALL_DIR"
fi

printf 'PASS  Node %s at %s\n' "$NODE_VERSION" "$INSTALL_DIR/bin/node"
