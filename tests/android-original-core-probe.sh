#!/system/bin/sh
set -eu
test "$#" -eq 5 || { printf 'usage: probe RUNTIME CORE BACKEND NODE_SHA MANIFEST_SHA\n'; exit 2; }
RUNTIME="$1"; CORE="$2"; BACKEND="$3"; NODE_SHA="$4"; MANIFEST_SHA="$5"
for path in "$RUNTIME" "$CORE" "$BACKEND"; do
  case "$path" in /*) ;; *) printf 'Absolute paths required\n'; exit 2;; esac
  case "$path" in *[!A-Za-z0-9_./-]*) printf 'Use an ASCII-only independent test directory\n'; exit 2;; esac
done
for hash in "$NODE_SHA" "$MANIFEST_SHA"; do
  test "${#hash}" -eq 64 || exit 2
  case "$hash" in *[!a-f0-9]*) exit 2;; esac
done
test -x "$RUNTIME/node"; test -x "$BACKEND"
test -f "$CORE/probe-original.mjs"; test -f "$CORE/verify-original-core.mjs"
ACTUAL=$(sha256sum "$RUNTIME/node"); test "${ACTUAL%% *}" = "$NODE_SHA"
ACTUAL=$(sha256sum "$CORE/manifest.json"); test "${ACTUAL%% *}" = "$MANIFEST_SHA"
ACTUAL=$(sha256sum "$BACKEND"); test "${ACTUAL%% *}" = 8e5696d97f8eef4aded6f48fa2be52543cba417570566044bbd0087ec6dac838
CASE=$(mktemp -d "$(dirname "$BACKEND")/c4-native.XXXXXXXX")
printf 'C4_TEST_DIR=%s\n' "$CASE"
mkdir "$CASE/home" "$CASE/tmp"
# The original code intentionally filters inherited LD_LIBRARY_PATH. Do not weaken it.
# DSH_TEST_NODE is an upstream-supported test override; this wrapper is only for fixtures.
{
  printf '#!/system/bin/sh\n'
  printf 'LD_LIBRARY_PATH="%s/lib"; export LD_LIBRARY_PATH\n' "$RUNTIME"
  printf 'exec "%s/node" "$@"\n' "$RUNTIME"
} > "$CASE/node-fixture-launcher"
chmod 700 "$CASE/node-fixture-launcher"
set +e
timeout -k 2 20 env -i PATH="$RUNTIME:/system/bin:/system/xbin" HOME="$CASE/home" TMPDIR="$CASE/tmp" LD_LIBRARY_PATH="$RUNTIME/lib" \
  "$RUNTIME/node" "$CORE/verify-original-core.mjs" "$CORE" "$MANIFEST_SHA" > "$CASE/payload-verification.jsonl" 2> "$CASE/payload-stderr.txt"
RC=$?
set -e
printf '%s\n' "$RC" > "$CASE/payload-exit.txt"
if test "$RC" -ne 0; then cat "$CASE/payload-stderr.txt"; exit "$RC"; fi
cat "$CASE/payload-verification.jsonl"
set +e
timeout -k 2 20 env -i PATH="$RUNTIME:/system/bin:/system/xbin" HOME="$CASE/home" TMPDIR="$CASE/tmp" LD_LIBRARY_PATH="$RUNTIME/lib" \
  "$RUNTIME/node" "$CORE/probe-original.mjs" "$BACKEND" > "$CASE/original-probe.jsonl" 2> "$CASE/probe-stderr.txt"
RC=$?
set -e
printf '%s\n' "$RC" > "$CASE/probe-exit.txt"
printf 'ORIGINAL_PROBE_EXIT=%s\n' "$RC"
cat "$CASE/original-probe.jsonl" "$CASE/probe-stderr.txt"
exit "$RC"
