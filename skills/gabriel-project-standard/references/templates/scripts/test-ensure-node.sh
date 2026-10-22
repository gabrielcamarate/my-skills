#!/usr/bin/env bash
# Regression cases for ensure-node.sh. A local file:// distribution with
# stub binaries stands in for nodejs.org, so the test needs no network.
set -Eeuo pipefail

ROOT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
ENSURE="$ROOT_DIR/scripts/ensure-node.sh"
WORK=$(mktemp -d)
trap 'rm -rf -- "$WORK"' EXIT
fail() { printf 'FAIL  %s\n' "$1" >&2; exit 1; }

PINNED=$(sed -n 's/^NODE_VERSION=//p' "$ENSURE")
OTHER=24.0.0
PLATFORM=linux-x64
NAME="node-v$PINNED-$PLATFORM"
BASE_PATH=/usr/bin:/bin

stub_node() { # dir version
  mkdir -p -- "$1"
  printf '#!/bin/sh\n[ "$1" = --version ] && echo v%s\n' "$2" > "$1/node"
  chmod +x "$1/node"
}

# Fake distribution laid out like nodejs.org/dist/v<version>/.
DIST="$WORK/dist"
publish() { # version
  local name="node-v$1-$PLATFORM"
  mkdir -p -- "$DIST/v$1" "$WORK/build/$name/bin"
  stub_node "$WORK/build/$name/bin" "$1"
  for tool in npm npx corepack; do printf '#!/bin/sh\necho %s\n' "$tool" > "$WORK/build/$name/bin/$tool"; chmod +x "$WORK/build/$name/bin/$tool"; done
  tar -czf "$DIST/v$1/$name.tar.gz" -C "$WORK/build" "$name"
  (cd "$DIST/v$1" && sha256sum "$name.tar.gz" > SHASUMS256.txt)
}
publish "$PINNED"
publish "$OTHER"
printf '%s  node-v%s-darwin-arm64.tar.gz\n' "$(printf x | sha256sum | cut -d' ' -f1)" "$PINNED" >> "$DIST/v$PINNED/SHASUMS256.txt"

stub_node "$WORK/old" 22.22.0
stub_node "$WORK/pinned" "$PINNED"

# A second project pinned to another version, sharing the same prefix.
mkdir -p -- "$WORK/project-b/scripts"
sed "s/^NODE_VERSION=.*/NODE_VERSION=$OTHER/" "$ENSURE" > "$WORK/project-b/scripts/ensure-node.sh"

run_script() { # script prefix path [args...]
  local script=$1 prefix=$2 path=$3; shift 3
  env -i HOME="$WORK/home" PATH="$path" NODE_PREFIX="$prefix" \
    NODE_DIST_URL="file://$DIST" NODE_DIST_PLATFORM="$PLATFORM" bash "$script" "$@"
}
run() { run_script "$ENSURE" "$@"; }
run_b() { run_script "$WORK/project-b/scripts/ensure-node.sh" "$@"; }

# Another version on PATH: installs the pinned build under the prefix only.
P1="$WORK/p1"
run "$P1" "$WORK/old:$BASE_PATH" >/dev/null || fail 'install with another Node on PATH'
BIN1=$(run "$P1" "$WORK/old:$BASE_PATH" --bin) || fail '--bin must print the pinned bin dir'
[[ "$BIN1" == "$P1/lib/pinned-node/$NAME/bin" ]] || fail "unexpected --bin output: $BIN1"
[[ $("$BIN1/node" --version) == "v$PINNED" ]] || fail 'pinned node is not the pinned version'
for tool in npm npx corepack; do [[ -x "$BIN1/$tool" ]] || fail "$tool missing from the pinned bin dir"; done
[[ ! -e "$P1/bin" ]] || fail 'must not create or touch the shared prefix bin dir'
[[ $(PATH="$BIN1:$WORK/old:$BASE_PATH" node --version) == "v$PINNED" ]] || fail 'pinned bin dir does not resolve node'

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
[[ -z $(ls -A "$P3/lib/pinned-node" 2>/dev/null) ]] || fail 'mismatch must not leave an install'

# Archive missing from SHASUMS256.txt fails closed.
grep -v " $NAME.tar.gz$" "$WORK/sums.ok" > "$DIST/v$PINNED/SHASUMS256.txt"
if out=$(run "$P3" "$WORK/old:$BASE_PATH" 2>&1); then fail 'missing checksum must fail'; fi
[[ "$out" == *'no SHA256'* ]] || fail "unexpected missing-checksum output: $out"
cp -- "$WORK/sums.ok" "$DIST/v$PINNED/SHASUMS256.txt"

# The shared prefix bin dir is never modified, whatever it holds.
P4="$WORK/p4"
stub_node "$P4/bin" 20.0.0
mkdir -p -- "$P4/lib/pinned-node"
ln -s "$P4/lib/pinned-node/node-v$OTHER-$PLATFORM/bin/npm" "$P4/bin/npm"
run "$P4" "$WORK/old:$BASE_PATH" >/dev/null || fail 'install must ignore the shared bin dir'
[[ $("$P4/bin/node" --version) == v20.0.0 ]] || fail 'foreign node was modified'
[[ $(readlink "$P4/bin/npm") == "$P4/lib/pinned-node/node-v$OTHER-$PLATFORM/bin/npm" ]] || fail 'existing link was repointed'

# Two projects with different pins install in parallel on one prefix and each
# process keeps its own version, even while the other project installs.
P5="$WORK/p5"
run "$P5" "$WORK/old:$BASE_PATH" >/dev/null || fail 'project A install'
BIN_A=$(run "$P5" "$WORK/old:$BASE_PATH" --bin)
BIN_B=$(run_b "$P5" "$WORK/old:$BASE_PATH" --bin)
run_b "$P5" "$WORK/old:$BASE_PATH" >"$WORK/b.log" 2>&1 & pid_b=$!
for _ in 1 2 3 4 5; do
  run "$P5" "$BIN_A:$WORK/old:$BASE_PATH" --check >/dev/null || fail 'project A lost its Node while B installed'
done
wait "$pid_b" || fail "project B install: $(cat "$WORK/b.log")"
run "$P5" "$BIN_A:$WORK/old:$BASE_PATH" --check >/dev/null || fail 'project A must still see its own Node'
run_b "$P5" "$BIN_B:$WORK/old:$BASE_PATH" --check >/dev/null || fail 'project B must see its own Node'
[[ ! -e "$P5/bin" ]] || fail 'parallel installs must not touch the shared bin dir'

# The same version installed by two sessions at once: both succeed.
P6="$WORK/p6"
run "$P6" "$WORK/old:$BASE_PATH" >"$WORK/a1.log" 2>&1 & pid1=$!
run "$P6" "$WORK/old:$BASE_PATH" >"$WORK/a2.log" 2>&1 & pid2=$!
wait "$pid1" || fail "concurrent install 1: $(cat "$WORK/a1.log")"
wait "$pid2" || fail "concurrent install 2: $(cat "$WORK/a2.log")"
[[ $("$P6/lib/pinned-node/$NAME/bin/node" --version) == "v$PINNED" ]] || fail 'concurrent installs left a broken Node'

# --check and --bin report without installing anything.
P7="$WORK/p7"
run "$P7" "$WORK/pinned:$BASE_PATH" --check >/dev/null || fail '--check must pass with the pinned Node'
if out=$(run "$P7" "$WORK/old:$BASE_PATH" --check 2>&1); then fail '--check must fail with another Node'; fi
[[ "$out" == *'v22.22.0'* && "$out" == *'--bin'* ]] || fail "unexpected --check output: $out"
run "$P7" "$WORK/old:$BASE_PATH" --bin >/dev/null || fail '--bin must not need an install'
[[ ! -e "$P7" ]] || fail '--check and --bin must not install'

# Only https:// (or file:// for tests) mirrors are accepted, before any download.
if out=$(env -i HOME="$WORK/home" PATH="$WORK/old:$BASE_PATH" NODE_PREFIX="$WORK/p-http" \
    NODE_DIST_URL="http://nodejs.org/dist" NODE_DIST_PLATFORM="$PLATFORM" bash "$ENSURE" 2>&1); then
  fail 'plain http mirror must be refused'
fi
[[ "$out" == *'https://'* && ! -e "$WORK/p-http" ]] || fail "unexpected http refusal: $out"

printf 'PASS  ensure-node\n'
