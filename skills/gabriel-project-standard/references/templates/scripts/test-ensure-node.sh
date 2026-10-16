#!/usr/bin/env bash
# Regression cases for ensure-node.sh (#510). A local file:// distribution with
# stub binaries stands in for nodejs.org, so the test needs no network.
set -Eeuo pipefail

ROOT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
ENSURE="$ROOT_DIR/scripts/ensure-node.sh"
WORK=$(mktemp -d)
trap 'rm -rf -- "$WORK"' EXIT
fail() { printf 'FAIL  %s\n' "$1" >&2; exit 1; }

PINNED=22.20.0
PLATFORM=linux-x64
NAME="node-v$PINNED-$PLATFORM"
BASE_PATH=/usr/bin:/bin

stub_node() { # dir version
  mkdir -p -- "$1"
  printf '#!/bin/sh\n[ "$1" = --version ] && echo v%s\n' "$2" > "$1/node"
  chmod +x "$1/node"
}

# Fake distribution laid out like nodejs.org/dist/v$PINNED/.
DIST="$WORK/dist"
mkdir -p -- "$DIST/v$PINNED" "$WORK/build/$NAME/bin"
stub_node "$WORK/build/$NAME/bin" "$PINNED"
for tool in npm npx corepack; do printf '#!/bin/sh\necho %s\n' "$tool" > "$WORK/build/$NAME/bin/$tool"; chmod +x "$WORK/build/$NAME/bin/$tool"; done
tar -czf "$DIST/v$PINNED/$NAME.tar.gz" -C "$WORK/build" "$NAME"
(cd "$DIST/v$PINNED" && sha256sum "$NAME.tar.gz" > SHASUMS256.txt)
printf '%s  node-v%s-darwin-arm64.tar.gz\n' "$(printf x | sha256sum | cut -d' ' -f1)" "$PINNED" >> "$DIST/v$PINNED/SHASUMS256.txt"

stub_node "$WORK/old" 22.22.0
stub_node "$WORK/pinned" "$PINNED"

run() { # prefix path [args...]
  local prefix=$1 path=$2; shift 2
  env -i HOME="$WORK/home" PATH="$path" NODE_PREFIX="$prefix" \
    NODE_DIST_URL="file://$DIST" NODE_DIST_PLATFORM="$PLATFORM" bash "$ENSURE" "$@"
}

# Another version on PATH: installs the pinned build under the prefix.
P1="$WORK/p1"
run "$P1" "$WORK/old:$BASE_PATH" >/dev/null || fail 'install with another Node on PATH'
[[ $("$P1/bin/node" --version) == "v$PINNED" ]] || fail 'prefix node is not the pinned version'
for tool in npm npx corepack; do [[ -x "$P1/bin/$tool" ]] || fail "$tool not linked"; done
[[ $(PATH="$P1/bin:$WORK/old:$BASE_PATH" node --version) == "v$PINNED" ]] || fail 'prefix bin does not resolve node'

# Idempotent: a second run reuses the install and never downloads.
mv -- "$DIST" "$DIST.off"
run "$P1" "$WORK/old:$BASE_PATH" >/dev/null || fail 'second run must reuse the existing install'
mv -- "$DIST.off" "$DIST"

# The pinned version already first on PATH: nothing is installed.
P2="$WORK/p2"
run "$P2" "$WORK/pinned:$BASE_PATH" >/dev/null || fail 'pinned Node on PATH must pass'
[[ ! -e "$P2" ]] || fail 'must not install when the pinned Node is already on PATH'

# Tampered archive: checksum mismatch fails closed and leaves nothing behind.
P3="$WORK/p3"
cp -- "$DIST/v$PINNED/SHASUMS256.txt" "$WORK/sums.ok"
sed -i "s/^[0-9a-f]\{64\}  $NAME.tar.gz$/$(printf y | sha256sum | cut -d' ' -f1)  $NAME.tar.gz/" "$DIST/v$PINNED/SHASUMS256.txt"
if out=$(run "$P3" "$WORK/old:$BASE_PATH" 2>&1); then fail 'checksum mismatch must fail'; fi
[[ "$out" == *'SHA256 mismatch'* ]] || fail "unexpected mismatch output: $out"
[[ ! -e "$P3/bin/node" && -z $(ls -A "$P3/lib/pinned-node" 2>/dev/null) ]] || fail 'mismatch must not leave an install'

# Archive missing from SHASUMS256.txt fails closed.
grep -v " $NAME.tar.gz$" "$WORK/sums.ok" > "$DIST/v$PINNED/SHASUMS256.txt"
if out=$(run "$P3" "$WORK/old:$BASE_PATH" 2>&1); then fail 'missing checksum must fail'; fi
[[ "$out" == *'no SHA256'* ]] || fail "unexpected missing-checksum output: $out"
cp -- "$WORK/sums.ok" "$DIST/v$PINNED/SHASUMS256.txt"

# Never replaces a node binary it does not own.
P4="$WORK/p4"
stub_node "$P4/bin" 20.0.0
if out=$(run "$P4" "$WORK/old:$BASE_PATH" 2>&1); then fail 'must refuse to overwrite a foreign node'; fi
[[ "$out" == *'refusing to replace'* ]] || fail "unexpected overwrite output: $out"
[[ $("$P4/bin/node" --version) == v20.0.0 ]] || fail 'foreign node was modified'
[[ ! -e "$P4/lib" ]] || fail 'must refuse before downloading'
P6="$WORK/p6"
mkdir -p -- "$P6/bin" && ln -s "$WORK/old/node" "$P6/bin/node"
if run "$P6" "$WORK/old:$BASE_PATH" >/dev/null 2>&1; then fail 'must refuse to replace a foreign symlink'; fi
[[ $(readlink "$P6/bin/node") == "$WORK/old/node" ]] || fail 'foreign symlink was modified'

# --check reports the version on PATH without installing anything.
run "$WORK/p5" "$WORK/pinned:$BASE_PATH" --check >/dev/null || fail '--check must pass with the pinned Node'
if out=$(run "$WORK/p5" "$WORK/old:$BASE_PATH" --check 2>&1); then fail '--check must fail with another Node'; fi
[[ "$out" == *'v22.22.0'* && "$out" == *'cloud-setup.sh'* ]] || fail "unexpected --check output: $out"
[[ ! -e "$WORK/p5" ]] || fail '--check must not install'

# Only https:// (or file:// for tests) mirrors are accepted, before any download.
if out=$(env -i HOME="$WORK/home" PATH="$WORK/old:$BASE_PATH" NODE_PREFIX="$WORK/p-http" \
    NODE_DIST_URL="http://nodejs.org/dist" NODE_DIST_PLATFORM="$PLATFORM" bash "$ENSURE" 2>&1); then
  fail 'plain http mirror must be refused'
fi
[[ "$out" == *'https://'* && ! -e "$WORK/p-http" ]] || fail "unexpected http refusal: $out"

printf 'PASS  ensure-node\n'
