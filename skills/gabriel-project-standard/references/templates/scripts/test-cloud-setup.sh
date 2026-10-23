#!/usr/bin/env bash
# Regression cases for cloud-setup.sh and ensure-pnpm.sh. A local file://
# Node distribution and stub npm/pnpm stand in for nodejs.org and the npm
# registry, so the test needs no network or package install.
set -Eeuo pipefail

ROOT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
WORK=$(mktemp -d)
trap 'rm -rf -- "$WORK"' EXIT
fail() { printf 'FAIL  %s\n' "$1" >&2; exit 1; }

PINNED=$(sed -n 's/^NODE_VERSION=//p' "$ROOT_DIR/scripts/ensure-node.sh")
PNPM_PINNED=$(sed -n 's/^PNPM_VERSION=//p' "$ROOT_DIR/scripts/ensure-pnpm.sh")
PLATFORM=linux-x64
NAME="node-v$PINNED-$PLATFORM"
BASE_PATH=/usr/bin:/bin

stub() { # file body
  mkdir -p -- "$(dirname -- "$1")"
  printf '#!/bin/sh\n%s\n' "$2" > "$1"
  chmod +x "$1"
}
stub_node() { stub "$1/node" "[ \"\$1\" = --version ] && echo v$2"; }

# Fake nodejs.org distribution. Its npm installs pnpm the way
# `npm install --global --prefix P pnpm@V` does: a launcher in P/bin that runs
# on whichever node comes first on PATH, like `#!/usr/bin/env node`.
DIST="$WORK/dist"
mkdir -p -- "$DIST/v$PINNED" "$WORK/build/$NAME/bin"
stub_node "$WORK/build/$NAME/bin" "$PINNED"
stub "$WORK/build/$NAME/bin/npm" "
echo \"npm node=\$(node --version) \$*\" >> '$WORK/npm.log'
[ ! -e '$WORK/npm-fails' ] || exit 1
sleep 1
while [ \$# -gt 0 ]; do case \$1 in --prefix) prefix=\$2; shift ;; pnpm@*) version=\${1#pnpm@} ;; esac; shift; done
mkdir -p \"\$prefix/bin\"
printf '#!/bin/sh\n[ \"\$1\" = --version ] && echo %s && exit 0\necho \"pnpm \$* node=\$(node --version)\" >> %s\n' \"\$version\" '$WORK/pnpm.log' > \"\$prefix/bin/pnpm\"
chmod +x \"\$prefix/bin/pnpm\""
tar -czf "$DIST/v$PINNED/$NAME.tar.gz" -C "$WORK/build" "$NAME"
(cd "$DIST/v$PINNED" && sha256sum "$NAME.tar.gz" > SHASUMS256.txt)

# Project copy: cloud-setup.sh finds its helpers beside it.
PROJECT="$WORK/project"
mkdir -p -- "$PROJECT/scripts"
cp -- "$ROOT_DIR/scripts/cloud-setup.sh" "$ROOT_DIR/scripts/ensure-node.sh" "$ROOT_DIR/scripts/ensure-pnpm.sh" "$PROJECT/scripts/"
chmod +x "$PROJECT"/scripts/*.sh

# Cloud container layout: the shared ~/.local/bin (the default prefix) holds
# another Node and another pnpm, first on PATH.
HOME_DIR="$WORK/home"
SHARED="$HOME_DIR/.local/bin"
stub_node "$SHARED" 22.22.0
stub "$SHARED/pnpm" "[ \"\$1\" = --version ] && echo 9.0.0 && exit 0
echo \"foreign pnpm \$*\" >> '$WORK/pnpm.log'; exit 1"
snapshot() { tar --sort=name -cf - -C "$SHARED" . | sha256sum; }
BEFORE=$(snapshot)

run_env() { # prefix-or-empty command...
  local prefix=$1; shift
  env -i HOME="$HOME_DIR" PATH="$SHARED:$BASE_PATH" ${prefix:+NODE_PREFIX="$prefix"} \
    NODE_DIST_URL="file://$DIST" NODE_DIST_PLATFORM="$PLATFORM" "$@"
}
run_setup() { run_env '' bash "$PROJECT/scripts/cloud-setup.sh"; }
npm_runs() { grep -c '^npm ' "$WORK/npm.log" 2>/dev/null || true; }

out=$(run_setup 2>&1) || fail "setup with another Node and pnpm in ~/.local/bin: $out"
[[ "$out" == *'PASS  environment ready'* ]] || fail "unexpected setup output: $out"
[[ $(npm_runs) == 1 ]] || fail "expected one pnpm install: $(cat "$WORK/npm.log")"
grep -q "^npm node=v$PINNED .*--prefix $HOME_DIR/.local/lib/pinned-pnpm/\.install\." "$WORK/npm.log" \
  || fail "pnpm must be installed by the pinned npm into pinned-pnpm: $(cat "$WORK/npm.log")"
[[ $(cat "$WORK/pnpm.log") == "pnpm install --frozen-lockfile node=v$PINNED" ]] \
  || fail "pnpm install must run on the pinned pnpm and Node: $(cat "$WORK/pnpm.log")"
[[ $("$HOME_DIR/.local/lib/pinned-pnpm/$PNPM_PINNED/bin/pnpm" --version) == "$PNPM_PINNED" ]] \
  || fail 'pinned pnpm missing'
[[ $(snapshot) == "$BEFORE" ]] || fail '~/.local/bin was modified'

# The second run reuses both installs: no download, no npm.
mv -- "$DIST" "$DIST.off"
out=$(run_setup 2>&1) || fail "second setup run: $out"
mv -- "$DIST.off" "$DIST"
[[ $(npm_runs) == 1 ]] || fail "second run reinstalled pnpm: $(cat "$WORK/npm.log")"
[[ $(snapshot) == "$BEFORE" ]] || fail '~/.local/bin was modified by the second run'

BIN=$(run_env '' bash "$PROJECT/scripts/ensure-node.sh" --bin)

# --check and --bin report without installing anything.
P1="$WORK/p1"
if out=$(run_env "$P1" bash "$PROJECT/scripts/ensure-pnpm.sh" --check 2>&1); then fail '--check must fail with another pnpm'; fi
[[ "$out" == *'found 9.0.0'* && "$out" == *'--bin'* ]] || fail "unexpected --check output: $out"
[[ $(run_env "$P1" bash "$PROJECT/scripts/ensure-pnpm.sh" --bin) == "$P1/lib/pinned-pnpm/$PNPM_PINNED/bin" ]] \
  || fail 'unexpected --bin output'
[[ ! -e "$P1" ]] || fail '--check and --bin must not install'

# Two sessions install the same version at once: one npm run, both succeed.
P2="$WORK/p2"
: > "$WORK/npm.log"
run_env "$P2" env PATH="$BIN:$SHARED:$BASE_PATH" bash "$PROJECT/scripts/ensure-pnpm.sh" >"$WORK/a1.log" 2>&1 & pid1=$!
run_env "$P2" env PATH="$BIN:$SHARED:$BASE_PATH" bash "$PROJECT/scripts/ensure-pnpm.sh" >"$WORK/a2.log" 2>&1 & pid2=$!
wait "$pid1" || fail "concurrent install 1: $(cat "$WORK/a1.log")"
wait "$pid2" || fail "concurrent install 2: $(cat "$WORK/a2.log")"
[[ $(npm_runs) == 1 ]] || fail "concurrent installs ran npm twice: $(cat "$WORK/npm.log")"
[[ $("$P2/lib/pinned-pnpm/$PNPM_PINNED/bin/pnpm" --version) == "$PNPM_PINNED" ]] || fail 'concurrent installs left a broken pnpm'

# A failed npm install fails closed and leaves nothing behind.
P3="$WORK/p3"
touch "$WORK/npm-fails"
if out=$(run_env "$P3" env PATH="$BIN:$SHARED:$BASE_PATH" bash "$PROJECT/scripts/ensure-pnpm.sh" 2>&1); then
  fail 'failed npm install must fail'
fi
rm -- "$WORK/npm-fails"
[[ "$out" == *"unable to install pnpm $PNPM_PINNED"* ]] || fail "unexpected npm failure output: $out"
[[ -z $(ls -A "$P3/lib/pinned-pnpm" | grep -v '^\.install\.lock$' || true) ]] || fail 'failed install left files behind'
[[ $(snapshot) == "$BEFORE" ]] || fail '~/.local/bin was modified'

printf 'PASS  cloud-setup\n'
